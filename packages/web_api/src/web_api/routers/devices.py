from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from ..dependencies import get_device_registry, get_ws_broker

router = APIRouter(
    prefix="/api/v1/fertility/devices",
    tags=["devices"],
)


@router.get(
    "/",
    summary="List devices",
    description="Returns all registered device adapters and their metadata.",
    responses={
        200: {"description": "List of devices"},
    },
)
async def list_devices():
    registry = get_device_registry()
    if registry is None:
        return {"devices": []}
    return {"devices": registry.list_adapters()}


@router.post(
    "/read",
    summary="Read all devices",
    description="Triggers a read from all connected devices and broadcasts readings via WebSocket.",
    responses={
        200: {"description": "Device readings"},
        503: {"description": "Device registry not available"},
    },
)
async def read_all_devices():
    registry = get_device_registry()
    if registry is None:
        raise HTTPException(status_code=503, detail="Device registry not available. Try again later.")
    readings = await registry.read_all()

    broker = get_ws_broker()
    if broker is not None and readings:
        from ..websocket import make_message

        adapters = registry.list_adapters()
        for adapter_info in adapters:
            device_id = adapter_info["device_id"]
            if device_id in readings:
                await broker.broadcast(
                    make_message(
                        "device_reading",
                        {
                            "profile_slug": "default",
                            "device_id": device_id,
                            "device_type": adapter_info["device_type"],
                            "temperature": readings[device_id],
                        },
                    )
                )

    return {"readings": readings}


@router.get(
    "/{device_id}/status",
    summary="Get device status",
    description="Returns the connection status and metadata for a specific device.",
    responses={
        200: {"description": "Device status"},
        404: {"description": "Device not found"},
        503: {"description": "Device registry not available"},
    },
)
async def get_device_status(device_id: str):
    registry = get_device_registry()
    if registry is None:
        raise HTTPException(status_code=503, detail="Device registry not available. Try again later.")
    adapter = registry.get_adapter(device_id)
    if adapter is None:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    connected = await adapter.is_connected()
    return {
        "device_id": device_id,
        "device_type": adapter.device_type,
        "connected": connected,
    }
