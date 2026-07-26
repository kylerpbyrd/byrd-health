# WebSocket Protocol Specification v1

> **Status:** Canonical | **Scope:** Phase 3+ | **Governed by:** ADR-0012  
> **Date:** 2026-07-26

---

## 1. Overview

This document defines the WebSocket message protocol used between the Byrd Health backend (`/api/v1/fertility/ws`) and all clients (frontend SPA, future mobile, future ByrdOS).

This is a **stable, versioned contract**. Breaking changes require a protocol version increment and backward-compatibility consideration.

---

## 2. Endpoint

```
ws://{host}/api/v1/fertility/ws
```

Connections are accepted by the `WebSocketBroker` (in-memory pub/sub, ADR-0012). The broker broadcasts messages to all connected clients. There is no client-to-server messaging path — the client is a passive receiver.

---

## 3. Message Envelope

Every message uses the same outer envelope:

```json
{
  "version": 1,
  "type": "<message_type>",
  "timestamp": "<ISO 8601 UTC>",
  "payload": { ... }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | `int` | Yes | Protocol version. Currently `1`. |
| `type` | `string` | Yes | Message type discriminator. See §4. |
| `timestamp` | `string` | Yes | ISO 8601 timestamp in UTC (e.g. `2026-07-26T12:00:00Z`). |
| `payload` | `object` | Yes | Type-specific payload. See §5. |

### 3.1 Versioning Strategy

- **Minor additions** (new `type` values, new payload fields with defaults): No version bump required. Clients ignore unknown fields.
- **Breaking changes** (field removal, type change, field rename): Increment `version`. The backend may support multiple versions during a transition window.
- **Deprecation:** A `type` may be deprecated with a notice period. Clients should handle unknown types gracefully.

---

## 4. Message Types

### 4.1 `device_reading`

Emitted when a device produces a new temperature reading. One message per device per reading.

**Emission points:**
- `POST /api/v1/fertility/devices/read` — after `DeviceRegistry.read_all()` completes
- Future: automatic polling adapter push

**Intent:** Populate the frontend entry form with the latest reading from a connected device. Show a toast notification on the dashboard.

### 4.2 `analysis_complete`

Emitted when cycle analysis completes after an entry is created or reanalysis is triggered.

**Emission points:**
- `POST /api/v1/fertility/entries/` — after entry creation triggers analysis
- `POST /api/v1/fertility/insights/reanalyze` — after explicit reanalysis

**Intent:** Tell the frontend to invalidate dashboard and chart queries so the user sees updated insights without manual refresh.

### 4.3 `error`

Reserved for future use. Not currently emitted.

### 4.4 Future Types

The protocol is designed to accommodate additional types without breaking changes:

| Type | Phase | Intent |
|------|-------|--------|
| `notification` | 4 | HA notification event forwarded to frontend |
| `entity_update` | 4 | HA entity state change relay |
| `sync` | ByrdOS | Multi-device sync event |
| `heartbeat` | 4 | Server keepalive (client already handles this via WebSocket ping/pong) |

---

## 5. Payload Schemas

### 5.1 `device_reading`

```json
{
  "version": 1,
  "type": "device_reading",
  "timestamp": "2026-07-26T12:00:00Z",
  "payload": {
    "profile_slug": "default",
    "device_id": "sensor.bbt_bedroom",
    "device_type": "ha_sensor",
    "temperature": 97.85
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `profile_slug` | `string` | The profile context (always `"default"` for single-profile Phase 3). |
| `device_id` | `string` | Unique device identifier (entity ID, MAC address, etc.). |
| `device_type` | `string` | Adapter type: `"ha_sensor"`, `"esphome"`, or `"bluetooth"`. |
| `temperature` | `number` | Temperature reading. Unit depends on profile configuration. |

### 5.2 `analysis_complete`

```json
{
  "version": 1,
  "type": "analysis_complete",
  "timestamp": "2026-07-26T12:00:00Z",
  "payload": {
    "profile_slug": "default"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `profile_slug` | `string` | The profile that was analyzed. |

### 5.3 `error`

```json
{
  "version": 1,
  "type": "error",
  "timestamp": "2026-07-26T12:00:00Z",
  "payload": {
    "code": "DEVICE_READ_FAILED",
    "message": "Failed to read from sensor.bbt_bedroom"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `code` | `string` | Machine-readable error code. |
| `message` | `string` | Human-readable error description. |

---

## 6. Client Implementation Requirements

### 6.1 Message Handling

1. Parse the outer envelope to extract `version` and `type`.
2. If `version` is unknown, log a warning and skip the message (do not crash).
3. Dispatch by `type` to a handler function.
4. If `type` is unknown, ignore the message silently.
5. Extract `payload` and pass to the type-specific handler.

### 6.2 TypeScript Types (Phase 3)

```typescript
interface WSEnvelope {
  version: number;
  type: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

interface DeviceReadingPayload {
  profile_slug: string;
  device_id: string;
  device_type: string;
  temperature: number;
}

interface AnalysisCompletePayload {
  profile_slug: string;
}
```

### 6.3 Backend Broadcast Helper (Python)

```python
from datetime import UTC, datetime

def make_message(msg_type: str, payload: dict) -> dict:
    return {
        "version": 1,
        "type": msg_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "payload": payload,
    }
```

---

## 7. Backend Emission Points

| Location | Trigger | Message | Profile Context |
|----------|---------|---------|-----------------|
| `routers/devices.py` — `read_all_devices()` | `POST /devices/read` | `device_reading` (one per adapter) | Active profile |
| `routers/entries.py` — `create_entry()` | `POST /entries/` | `analysis_complete` | Active profile |
| `routers/insights.py` — `reanalyze_insights()` | `POST /insights/reanalyze` | `analysis_complete` | Active profile |

---

## 8. Backward Compatibility

### v1 Initial (Phase 3)

This version is the protocol baseline. No backward compatibility concerns.

### Future v2 (if needed)

If a breaking change is required:
- Backend supports both v1 and v2 simultaneously for a transition window.
- v1 messages continue to use `"version": 1`.
- v2 messages use `"version": 2`.
- Clients negotiate the version via a query parameter on connect: `?protocol_version=2`.
- If no version is specified, v1 is assumed.
- v1 support is dropped in a subsequent major release.

---

## 9. Governance

- This document is the **canonical source** for the WebSocket protocol.
- Changes require an ADR or an amendment to this document.
- The frontend TypeScript types and backend broadcast code must both conform to this document.
- Contract verification runs against this document, not against a specific implementation.
- ADR-0012 (WebSocket Architecture) governs the transport and broker. This document governs the message format.

---

## 10. References

- `ADR-0012` — WebSocket Architecture (transport, broker, Ingress compatibility)
- `ADR-0011` — Device Adapter Pattern (device types, registry)
- `docs/PHASE3_EXECUTION_PLAN.md` — Phase 3 contract alignment tasks
- `packages/web_api/src/web_api/routers/ws.py` — WebSocket endpoint
- `packages/web_api/src/web_api/websocket.py` — WebSocketBroker
- `frontend/src/hooks/useWebSocket.ts` — Frontend WebSocket client
