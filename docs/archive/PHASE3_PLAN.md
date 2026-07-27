# Phase 3 Implementation Plan — Device Integration & Real-Time

> Status: Proposed | Date: 2026-07-26 | Phase 2: Complete

---

## 1. Phase 3 Overview

**Objective:** Add automatic data ingestion from external devices and real-time updates. No device requires cloud connectivity — all local.

**Exit Criteria:**
- At least one device adapter is functional end-to-end
- WebSocket endpoint serves real-time device readings
- Frontend dashboard updates live without manual refresh
- Device registry is configurable via add-on options
- No new cloud dependencies introduced

---

## 2. Milestones

### P3-M1: Device Adapter Infrastructure
**Complexity:** Low | **Dependencies:** Phase 2 core platform

| Task | Agent | Deliverables |
|---|---|---|
| P3-M1.1 | Create `packages/device_adapters/` package | Backend Engineer | Package scaffold + protocol |
| P3-M1.2 | Implement `DeviceAdapter` protocol | Backend Engineer | `protocol.py` with typed interface |
| P3-M1.3 | Implement `DeviceRegistry` | Backend Engineer | `registry.py` — register, unregister, read_all |
| P3-M1.4 | Lift existing HA sensor polling into adapter | HA Engineer | `ha_sensor.py` adapter wrapping existing poller |
| P3-M1.5 | Write adapter tests | QA Engineer | Mock adapters, registry CRUD |

### P3-M2: WebSocket Infrastructure
**Complexity:** Medium | **Dependencies:** P3-M1

| Task | Agent | Deliverables |
|---|---|---|
| P3-M2.1 | Implement `WebSocketBroker` | Backend Engineer | `web_api/websocket.py` — pub/sub broker |
| P3-M2.2 | Add `/ws` endpoint | Backend Engineer | FastAPI WebSocket route |
| P3-M2.3 | Wire broker into app lifespan | Backend Engineer | Startup/shutdown hooks |
| P3-M2.4 | Add broker to device registry | Backend Engineer | Devices broadcast readings through broker |
| P3-M2.5 | Write WebSocket tests | QA Engineer | Connection, broadcast, disconnect, reconnect |
| P3-M2.6 | Verify Ingress WebSocket passthrough | QA Engineer | Test through HA Ingress proxy |

### P3-M3: ESPHome Integration
**Complexity:** Medium | **Dependencies:** P3-M1

| Task | Agent | Deliverables |
|---|---|---|
| P3-M3.1 | Implement ESPHome native API client | HA Engineer | `esphome.py` adapter — connect, read sensor |
| P3-M3.2 | Add ESPHome device config schema | HA Engineer | config.yaml device options |
| P3-M3.3 | Implement auto-discovery | HA Engineer | Scan HA entities for ESPHome devices |
| P3-M3.4 | Write ESPHome adapter tests | QA Engineer | Simulated ESPHome device |

### P3-M4: Bluetooth Thermometer Integration
**Complexity:** High | **Dependencies:** P3-M1

| Task | Agent | Deliverables |
|---|---|---|
| P3-M4.1 | Research BLE GATT profiles for BBT thermometers | Architect | `docs/research/bt-thermometers.md` |
| P3-M4.2 | Implement BLE scanner and GATT client | HA Engineer | `bluetooth.py` adapter |
| P3-M4.3 | Implement device pairing and reconnection | HA Engineer | Connection lifecycle management |
| P3-M4.4 | Add Bluetooth device config schema | HA Engineer | Device address, name, auto-connect |
| P3-M4.5 | Write Bluetooth adapter tests | QA Engineer | Simulated BLE peripheral |

### P3-M5: Frontend Real-Time
**Complexity:** Low | **Dependencies:** P3-M2

| Task | Agent | Deliverables |
|---|---|---|
| P3-M5.1 | Add WebSocket client to frontend | Frontend Engineer | `hooks/useWebSocket.ts` — connect, reconnect, message handler |
| P3-M5.2 | Live dashboard updates | Frontend Engineer | Dashboard re-renders on device reading push |
| P3-M5.3 | Device status indicator | Frontend Engineer | Connected/disconnected badge on dashboard |
| P3-M5.4 | Auto-fill entry form from device reading | Frontend Engineer | Pre-populate temperature field |

### P3-M6: Wearable APIs (Future)
**Complexity:** High | **Dependencies:** P3-M1

Deferred to Phase 4 pending ByrdOS integration. Wearable APIs (Apple Health, Google Health Connect, Oura) require OAuth credential management that is better suited for ByrdOS than an HA add-on.

| Task | Phase | Notes |
|---|---|---|
| Apple HealthKit | 4 | Requires iOS companion app |
| Google Health Connect | 4 | Requires Android companion app |
| Oura Ring API | 4 | Cloud API — violates privacy-first without ByrdOS mediation |
| Fitbit API | 4 | Cloud API — same concern |

---

## 3. Execution Order

```
P3-M1 (Adapter Infrastructure) ──────────────────────┐
     │                                                 │
     ├──► P3-M2 (WebSocket) ──┐                       │
     │                         ├──► P3-M5 (Frontend)   │
     ├──► P3-M3 (ESPHome) ─────┤                       │
     │                         │                       │
     └──► P3-M4 (Bluetooth) ───┘                       │
                                                       │
P3-M1 and P3-M2 are the critical path — everything else depends on them.
P3-M3 and P3-M4 can run in parallel after P3-M1.
P3-M5 runs after P3-M2.
```

---

## 4. Device Configuration (Proposed)

Add to `config.yaml`:

```yaml
devices:
  - name: "Bedroom Thermometer"
    type: ha_sensor
    entity_id: sensor.ble_temperature_bedroom
    poll_interval_seconds: 300

  - name: "Tempdrop"
    type: bluetooth
    address: "00:11:22:33:44:55"
    auto_connect: true

  - name: "ESP32 BBT Sensor"
    type: esphome
    host: "esp32-bbt.local"
    port: 6053
```

---

## 5. Agent Assignments

| Agent | Milestones | Primary Deliverables |
|---|---|---|
| Backend Engineer | P3-M1, P3-M2 | Adapter protocol, registry, WebSocket broker |
| HA Engineer | P3-M3, P3-M4 | ESPHome adapter, Bluetooth adapter |
| Frontend Engineer | P3-M5 | WebSocket client, live dashboard |
| QA Engineer | All | Adapter tests, WebSocket tests, integration tests |
| Architect | P3-M4.1 | Bluetooth research, ADR-0011, ADR-0012 |

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BLE stack unavailable on HA | Medium | High | Detect at startup; disable Bluetooth adapters gracefully |
| ESPHome API changes | Low | Medium | Pin to tested ESPHome version |
| Bluetooth pairing UX poor | High | Medium | Provide clear error messages; fallback to manual entry |
| WebSocket disconnects on HA restart | Medium | Low | Auto-reconnect with exponential backoff |
| Wearable API rate limits | High | Low | Deferred to Phase 4 (no cloud deps yet) |
