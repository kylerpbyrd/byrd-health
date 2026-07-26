from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..dependencies import get_ws_broker

router = APIRouter(
    prefix="/api/v1/fertility",
    tags=["websocket"],
)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    broker = get_ws_broker()
    if broker is None:
        await ws.close(code=1011)
        return
    await broker.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await broker.disconnect(ws)
