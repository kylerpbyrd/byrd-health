# Dependency Graph

> **Date:** 2026-07-26 | **Architecture:** ADR-0001

---

## Runtime Dependency Flow

```
                    ┌──────────────────┐
                    │    FRONTEND      │
                    │  React 18+ SPA   │
                    │  (Vite build)    │
                    └────────┬─────────┘
                             │ HTTP REST + WebSocket
                             │ (/api/v1/fertility/*)
                             ▼
                    ┌──────────────────┐
                    │    WEB API       │
                    │  FastAPI Gateway │
                    │  (orchestrator)  │
                    └──┬───┬───┬───┬──┘
                       │   │   │   │
          ┌────────────┘   │   │   └──────────────┐
          ▼                │   │                  ▼
┌──────────────────┐       │   │     ┌──────────────────────┐
│  FERTILITY       │       │   │     │   DEVICE ADAPTERS    │
│  ENGINE          │       │   │     │  (Protocol-based)    │
│  Pure Python     │       │   │     │                      │
│  Zero framework  │       │   │     │  HASensorAdapter     │
│  deps            │       │   │     │  ESPHomeAdapter      │
└──────────────────┘       │   │     │  BluetoothAdapter    │
                           │   │     └──────────┬───────────┘
                           │   │                │
          ┌────────────────┘   │                │ imports HAClient
          ▼                    │                ▼
┌──────────────────┐           │     ┌──────────────────────┐
│  DATA SERVICE    │           │     │    HA BRIDGE         │
│  SQLAlchemy 2.0  │           │     │  (HA-only package)   │
│  Alembic         │           │     │                      │
│  AES-256-GCM     │           │     │  Entity publishing    │
│  SQLite→PG path  │           │     │  Sensor polling      │
└──────────────────┘           │     │  IngressMiddleware   │
                               │     │  Notifications       │
                               │     │  Lovelace card       │
                               └─────│──────────────────────┘
                                     │ imports HABridge
                                     │ (composition root — accepted exception)
                                     │
                                     │ Protocol dependency:
                                     │ web_api → HABridgeProtocol
                                     │ (all non-composition-root code)
```

---

## Package Dependency Matrix

| | fertility_engine | data_service | ha_bridge | device_adapters | web_api | frontend |
|---|---|---|---|---|---|---|
| **fertility_engine** | — | ❌ | ❌ | ❌ | ❌ | ❌ |
| **data_service** | ❌ | — | ❌ | ❌ | ❌ | ❌ |
| **ha_bridge** | ❌ | ❌ | — | ❌ | ❌ | ❌ |
| **device_adapters** | ❌ | ❌ | ✅ | — | ❌ | ❌ |
| **web_api** | ✅ | ✅ | ✅ | ✅ | — | ❌ |
| **frontend** | HTTP only | HTTP only | HTTP only | HTTP only | HTTP+WS | — |

**Key:**
- ✅ = declared dependency (imports modules from that package)
- ❌ = no dependency (no imports, or HTTP-only communication)
- HTTP only = communicates exclusively through REST/WebSocket endpoints

---

## External Dependencies

### fertility_engine
```
pydantic >= 2.0
```

### data_service
```
sqlalchemy >= 2.0
alembic >= 1.13
aiosqlite >= 0.19
pydantic >= 2.0
cryptography >= 42.0  (→ bump to ≥44.0)
```

### ha_bridge
```
httpx >= 0.27
pydantic >= 2.0
```

### device_adapters
```
ha-bridge (internal)
bleak (optional — Bluetooth only)
```

### web_api
```
fastapi >= 0.110
uvicorn[standard] >= 0.29
pydantic >= 2.0
pydantic-settings >= 2.0
sqlalchemy >= 2.0
fertility-engine (internal)
data-service (internal)
device-adapters (internal)
ha-bridge (internal)
```

### frontend
```
react, react-dom (^18.3)
react-router-dom (^6.26)
@tanstack/react-query (^5.51)
recharts (^2.12)
tailwindcss (^3.4)
lucide-react (^0.400)
sonner (^2.0.7)
```

---

## Data Flow

```
User enters temperature
        │
        ▼
POST /api/v1/fertility/entries/
        │
        ├──> data_service.upsert_temperature()
        ├──> data_service.upsert_signs()
        ├──> data_service.upsert_symptoms()
        │
        ▼
fertility_engine.analyze_cycle()
        │
        ├──> coverline.compute_coverline()
        ├──> ovulation.detect_ovulation()
        ├──> fertile_window.compute_fertile_window()
        │
        ▼
data_service.upsert_insights()
        │
        ├──> ha_bridge.publish_insights()  ──> HA entities updated
        └──> WebSocketBroker.broadcast()    ──> Frontend live update
                │
                ▼
        Frontend invalidates dashboard query
        → BBT chart re-renders
        → Toast notification appears
```

---

## WebSocket Message Flow

```
DeviceAdapter.read_temperature()
        │
        ▼
DeviceRegistry.read_all()
        │
        ▼
POST /api/v1/fertility/devices/read
        │
        ├──> HTTP response: {"readings": {"sensor.bbt": 97.5}}
        └──> WebSocketBroker.broadcast({
                 version: 1,
                 type: "device_reading",
                 payload: {
                     profile_slug: "default",
                     device_id: "sensor.bbt",
                     device_type: "ha_sensor",
                     temperature: 97.5
                 }
             })
                │
                ▼
        Frontend useWebSocket hook
                │
                ├──> EntryPage: auto-fill temperature field
                └──> DashboardPage: toast notification
```

---

## Test Coverage by Package

| Package | Test Files | Approx. Tests | Covers |
|---|---|---|---|
| fertility_engine | 4 | ~25 | Algorithms: coverline, ovulation, fertile window, analysis |
| data_service | 3 | ~45 | Models, repositories, migrations |
| web_api | 7 | ~75 | REST endpoints, WebSocket, devices |
| ha_bridge | 5 | ~60 | Bridge, client, entities, notifications, poller |
| device_adapters | 4 | ~50 | Protocol, registry, bluetooth, esphome, ha_sensor |
| **Total** | **23** | **255** | |

---

## Architecture Decision Records

| ADR | Title | Status | Governs |
|---|---|---|---|
| 0001 | Platform Architecture | Accepted | All packages |
| 0002 | Frontend Architecture | Accepted | frontend |
| 0003 | Database Strategy | Accepted | data_service |
| 0004 | User/Profile Model | Accepted | data_service |
| 0005 | Legacy Migration Strategy | Accepted | tools/legacy-migrate |
| 0006 | HA Integration Boundary | Accepted | ha_bridge, web_api |
| 0007 | AI/Prediction Architecture | Accepted | fertility_engine |
| 0008 | Security & Privacy Model | Accepted | data_service, ha_bridge |
| 0009 | Testing Strategy | Accepted | All packages |
| 0010 | Graphify Knowledge Architecture | Accepted | graph/ |
| 0011 | Device Adapter Pattern | Accepted | device_adapters |
| 0012 | WebSocket Architecture | Accepted | web_api |
| 0013 | HA Container Distribution | Accepted | repository/, Dockerfile |

---

## Isolation Boundaries (ADR-0006)

```
ALLOWED:        ha_bridge ──> httpx (HA API calls)
                device_adapters ──> ha_bridge (HAClient)
                web_api (composition root) ──> ha_bridge (concrete HABridge)

FORBIDDEN:      fertility_engine ──> any other package
                data_service ──> any other package
                ha_bridge ──> web_api
                ha_bridge ──> fertility_engine
                ha_bridge ──> data_service
                frontend ──> any Python package (HTTP only)

ACCEPTED EXCEPTION: web_api/app.py imports concrete HABridge (composition root)
```
