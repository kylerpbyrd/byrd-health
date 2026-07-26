# ADR-0012: WebSocket Architecture

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Proposed                                       |
| **Date**     | 2026-07-26                                     |
| **Deciders** | Lead Architect                                 |
| **Replaces** | None                                           |
| **Scope**    | Real-time communication architecture           |

---

## 1. Context

The architecture documentation (`ARCHITECTURE.md`, `ADR-0006`) references a WebSocket endpoint at `/api/v1/fertility/ws` for real-time updates. This endpoint does not exist yet.

Phase 3 introduces device integrations that produce real-time data (Bluetooth thermometers streaming readings, ESPHome sensors pushing state changes). The frontend would benefit from live updates without polling.

Requirements:
- WebSocket endpoint at `/api/v1/fertility/ws`
- Real-time device readings pushed to frontend
- HA entity state changes relayed to internal subscribers
- Must work through HA Ingress proxy (WebSocket upgrade)
- Must not require the frontend to know about device protocols

## 2. Decision

Implement a **pub/sub WebSocket architecture** using FastAPI's built-in WebSocket support with a lightweight broker pattern.

### 2.1 Architecture

```
Device Adapter ──► DeviceRegistry ──► WebSocketBroker ──► Frontend
                                                │
HA Bridge (polling) ────────────────────────────┘
```

### 2.2 WebSocket Broker

A singleton `WebSocketBroker` manages connections and message routing:

```python
# packages/web_api/src/web_api/websocket.py

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
```

### 2.3 Message Protocol

```json
{
  "type": "device_reading" | "entity_update" | "analysis_complete" | "error",
  "payload": {
    "profile_slug": "default",
    "timestamp": "2026-07-26T12:00:00Z",
    "data": { ... }
  }
}
```

### 2.4 Endpoint

```python
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    broker = get_ws_broker()
    await broker.connect(ws)
    try:
        while True:
            # Keep alive — client sends pings, server responds
            await ws.receive_text()
    except WebSocketDisconnect:
        await broker.disconnect(ws)
```

### 2.5 Ingress Compatibility

The existing `IngressMiddleware` (in `web_api/ingress.py`) already passes through non-HTTP connections:

```python
if scope["type"] != "http":
    await self._app(scope, receive, send)
    return
```

WebSocket upgrades are type `"websocket"` in ASGI, so the middleware passes them through unchanged. The HA Ingress proxy supports WebSocket upgrades natively.

### 2.6 Wiring

The broker is wired into the app lifespan (like the HA Bridge):

```python
# lifespan
broker = WebSocketBroker()
set_ws_broker(broker)
# ... bridge and adapters broadcast through broker ...
yield
# cleanup
```

## 3. Consequences

### Positive
- No external dependencies (built on FastAPI WebSocket)
- Works through HA Ingress without special configuration
- Lightweight (in-memory, no Redis/MQTT needed for single-user HA)
- Same pattern extends to ByrdOS (just swap the broker backend if needed)
- Frontend gets real-time updates without polling

### Negative
- Single process only (no horizontal scaling) — acceptable for HA add-on
- In-memory broker loses state on restart — messages are ephemeral, which is acceptable
- Additional connection overhead per browser tab

### Risks
- HA Ingress WebSocket timeout differs by HA version — mitigated by client-side ping/pong
- Browser tab count could cause connection bloat — mitigated by per-profile deduplication
- Future ByrdOS multi-user needs a proper message queue — mitigated by the broker abstraction

## 4. Phase Timing

| Phase | WebSocket Scope |
|-------|----------------|
| 3.1   | Basic WebSocket endpoint + broker (infrastructure only) |
| 3.2   | Device reading push (when device produces a new reading) |
| 3.3   | Frontend real-time dashboard (live chart updates) |
| 4     | ByrdOS multi-user message queue (Redis/RabbitMQ backend) |

## 5. References

- `ADR-0006 §2.1` — WebSocket relay listed as Phase 3 HA Bridge responsibility
- `ADR-0001` — Platform architecture (API Gateway includes WebSocket)
- `ARCHITECTURE.md` — References `/api/v1/fertility/ws` endpoint
- `ADR-0011` — Device Adapter Pattern (adapters broadcast through broker)
