"""In-memory pub/sub WebSocket broker for real-time device updates.

Architecture: ADR-0012
"""

from datetime import UTC, datetime

from fastapi import WebSocket


def make_message(msg_type: str, payload: dict) -> dict:
    return {
        "version": 1,
        "type": msg_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "payload": payload,
    }


class WebSocketBroker:
    """In-memory pub/sub broker for WebSocket connections."""

    def __init__(self):
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)

    async def broadcast(self, message: dict) -> None:
        dead: set[WebSocket] = set()
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        self._connections -= dead

    @property
    def connection_count(self) -> int:
        return len(self._connections)
