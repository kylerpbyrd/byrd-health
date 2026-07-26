from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..dependencies import get_device_registry, get_ws_broker

router = APIRouter(
    prefix="/api/v1/fertility/devices",
    tags=["devices"],
)


@router.get("/")
async def list_devices():
    registry = get_device_registry()
    if registry is None:
        return {"devices": []}
    return {"devices": registry.list_adapters()}


@router.post("/read")
async def read_all_devices():
    registry = get_device_registry()
    if registry is None:
        raise HTTPException(status_code=503, detail="Device registry not available")

    readings = await registry.read_all()

    broker = get_ws_broker()
    if broker is not None and readings:
        await broker.broadcast(
            {
                "type": "device_reading",
                "payload": {
                    "profile_slug": "default",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": readings,
                },
            }
        )

    return {"readings": readings}


@router.get("/{device_id}/status")
async def get_device_status(device_id: str):
    registry = get_device_registry()
    if registry is None:
        raise HTTPException(status_code=503, detail="Device registry not available")

    adapter = registry.get_adapter(device_id)
    if adapter is None:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    connected = await adapter.is_connected()
    return {
        "device_id": device_id,
        "device_type": adapter.device_type,
        "connected": connected,
    }
