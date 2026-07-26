# Phase 3 Execution Plan

> **Status:** Authorized | **Phase 2:** Complete (RC1) | **ADRs:** 0011, 0012 Accepted  
> **Date:** 2026-07-25

---

## 1. Authorization

Phase 3 is authorized per the following decisions:

| Decision | Status |
|---|---|
| ADR-0011 — Device Adapter Pattern | Accepted |
| ADR-0012 — WebSocket Architecture | Accepted |
| Release handoff to Release Engineer | In progress |
| Quick Wins Q1-Q3 | Authorized (parallel) |

---

## 2. Pre-Flight Checklist

Before any Phase 3 implementation begins:

- [ ] Release Engineer certifies Phase 2 RC1 (pass verdict)
- [ ] Q1: HABridgeProtocol implemented (removes direct `ha_bridge` import from `web_api`)
- [ ] Q2: Mypy path conflict resolved (`--explicit-package-bases`)
- [ ] Q3: Frontend code-split (route-based lazy loading)
- [ ] Updated ADR index (`docs/adr/`)
- [ ] Updated Graphify graph (`graph/edges.json`, `graph/index.json`, node files)
- [ ] `PHASE3_EXECUTION_PLAN.md` exists (this document)

---

## 3. Milestone Execution Order

```
Phase 2 RC1 Validated
        │
        ▼
P3-M1: Device Adapter Infrastructure ──────────── (Backend Engineer)
        │
   ┌────┼────────────┬────────────────┐
   ▼    ▼            ▼                ▼
P3-M2: WebSocket   P3-M3: ESPHome   P3-M4: Bluetooth
(BE+QA)            (HA Eng+QA)      (HA Eng+QA)
   │
   ▼
P3-M5: Frontend Real-Time (FE+QA)
```

**Critical path:** P3-M1 → P3-M2 → P3-M5  
**Parallel:** P3-M3 and P3-M4 can run concurrently after P3-M1 completes  
**Deferred:** P3-M6 (Wearable APIs) — Phase 4

---

## 4. Milestone Details

### P3-M1: Device Adapter Infrastructure

| Attribute | Value |
|---|---|
| **Owner** | Backend Engineer |
| **Complexity** | Low |
| **Dependencies** | Phase 2 core platform |
| **Deliverables** | `packages/device_adapters/`, protocol, registry, HA sensor adapter, tests |

**Tasks:**

| # | Task | Agent | Artifacts | Acceptance |
|---|---|---|---|---|
| P3-M1.1 | Scaffold `packages/device_adapters/` package | Backend Engineer | `pyproject.toml`, `__init__.py`, `src/device_adapters/` | Package is pip-installable, imports work |
| P3-M1.2 | Implement `DeviceAdapter` protocol | Backend Engineer | `protocol.py` — typed `Protocol` with `device_id`, `device_type`, `connect`, `disconnect`, `read_temperature`, `is_connected` | Protocol passes `isinstance` check with mock adapter |
| P3-M1.3 | Implement `DeviceRegistry` | Backend Engineer | `registry.py` — `register`, `unregister`, `read_all` | Register/unregister/read tested with mock adapters |
| P3-M1.4 | Lift existing HA sensor polling into adapter | HA Engineer | `adapters/ha_sensor.py` — wraps existing HA entity polling into DeviceAdapter contract | Existing HA polling works unchanged, now through adapter interface |
| P3-M1.5 | Write adapter tests | QA Engineer | `tests/test_protocol.py`, `tests/test_registry.py`, `tests/test_ha_sensor.py` | Mock adapters, registry CRUD, HA sensor adapter coverage |

**Architecture rules:**
- NO breaking changes to existing HA functionality
- NO new dependencies in fertility_engine or data_service
- Privacy-first: no cloud deps
- Preserve HA add-on compatibility

---

### P3-M2: WebSocket Infrastructure

| Attribute | Value |
|---|---|
| **Owner** | Backend Engineer |
| **Complexity** | Medium |
| **Dependencies** | P3-M1 (device registry needed for broadcast source) |

**Tasks:**

| # | Task | Agent | Artifacts | Acceptance |
|---|---|---|---|---|
| P3-M2.1 | Implement `WebSocketBroker` | Backend Engineer | `web_api/websocket.py` — `WebSocketBroker` class with `connect`, `disconnect`, `broadcast` | Unit tests: connect/disconnect cycle, broadcast to N clients |
| P3-M2.2 | Add `/ws` endpoint | Backend Engineer | FastAPI WebSocket route at `/api/v1/fertility/ws` | WebSocket handshake succeeds, client receives JSON |
| P3-M2.3 | Wire broker into app lifespan | Backend Engineer | Startup: create broker singleton. Shutdown: close connections. | Broker available via `get_ws_broker()` dependency |
| P3-M2.4 | Integrate broker with device registry | Backend Engineer | Devices broadcast readings through broker on `read_all()` | Device reading appears at connected WebSocket client |
| P3-M2.5 | Write WebSocket tests | QA Engineer | `tests/test_websocket.py` — connection, broadcast, disconnect, reconnect | Multiple concurrent clients, message ordering, cleanup |
| P3-M2.6 | Verify Ingress WebSocket passthrough | QA Engineer | Test through HA Ingress proxy (`192.168.1.44:8123`) | WebSocket upgrade works through Ingress |

**Message protocol:**

```json
{
  "type": "device_reading" | "entity_update" | "analysis_complete" | "error",
  "payload": {
    "profile_slug": "default",
    "timestamp": "2026-07-25T12:00:00Z",
    "data": {}
  }
}
```

---

### P3-M3: ESPHome Integration

| Attribute | Value |
|---|---|
| **Owner** | HA Engineer |
| **Complexity** | Medium |
| **Dependencies** | P3-M1 (DeviceAdapter protocol), P3-M2 (WebSocket broker for push) |
| **Runs parallel to** | P3-M4 |

**Tasks:**

| # | Task | Agent | Artifacts | Acceptance |
|---|---|---|---|---|
| P3-M3.1 | Implement ESPHome native API client adapter | HA Engineer | `adapters/esphome.py` — `ESPHomeAdapter(DeviceAdapter)`, native API connection, sensor reading | Connect to ESPHome device, read sensor, parse value |
| P3-M3.2 | Add ESPHome device config schema | HA Engineer | Device options in `config.yaml` (host, port, name) | Configuration parsed at startup |
| P3-M3.3 | Implement auto-discovery | HA Engineer | Scan HA entities for ESPHome devices, offer as config suggestions | Running ESPHome devices detected |
| P3-M3.4 | Write ESPHome adapter tests | QA Engineer | `tests/test_esphome.py` — simulated ESPHome device, connect, read, disconnect | Full lifecycle with mock ESPHome API |

---

### P3-M4: Bluetooth Thermometer Integration

| Attribute | Value |
|---|---|
| **Owner** | HA Engineer |
| **Complexity** | High |
| **Dependencies** | P3-M1 (DeviceAdapter protocol) |
| **Runs parallel to** | P3-M3 |

**Tasks:**

| # | Task | Agent | Artifacts | Acceptance |
|---|---|---|---|---|
| P3-M4.1 | Research BLE GATT profiles for BBT thermometers | Architect (pre-work) | `docs/research/bt-thermometers.md` | Documented GATT services/characteristics for common BBT thermometers |
| P3-M4.2 | Implement BLE scanner and GATT client adapter | HA Engineer | `adapters/bluetooth.py` — `BluetoothAdapter(DeviceAdapter)`, BLE scan, GATT read | Discover device, connect, read temperature characteristic |
| P3-M4.3 | Implement device pairing and reconnection logic | HA Engineer | Connection lifecycle: scan → connect → read → disconnect → reconnect on failure | Survives device power cycle, HA restart |
| P3-M4.4 | Add Bluetooth device config schema | HA Engineer | Device address, name, auto-connect flag in config | Configuration parsed at startup |
| P3-M4.5 | Write Bluetooth adapter tests | QA Engineer | `tests/test_bluetooth.py` — simulated BLE peripheral, scan, connect, read, reconnect | Full lifecycle with mock BLE stack |

**Risk:** BLE stack availability varies across HA Supervisor versions. Mitigation: detect at startup, disable Bluetooth adapters gracefully if unavailable.

---

### P3-M5: Frontend Real-Time

| Attribute | Value |
|---|---|
| **Owner** | Frontend Engineer |
| **Complexity** | Low |
| **Dependencies** | P3-M2 (WebSocket endpoint) |

**Tasks:**

| # | Task | Agent | Artifacts | Acceptance |
|---|---|---|---|---|
| P3-M5.1 | Add WebSocket client to frontend | Frontend Engineer | `hooks/useWebSocket.ts` — connect, auto-reconnect with exponential backoff, message handler | WebSocket connects, survives disconnect/reconnect |
| P3-M5.2 | Live dashboard updates | Frontend Engineer | Dashboard re-renders on `device_reading` push | Temperature appears on chart without manual refresh |
| P3-M5.3 | Device status indicator | Frontend Engineer | Connected/disconnected badge on dashboard, last reading timestamp | Visual feedback when device is connected vs. offline |
| P3-M5.4 | Auto-fill entry form from device reading | Frontend Engineer | Pre-populate temperature field when new reading arrives | Entry form opens with latest device reading pre-filled |

---

## 5. Agent Assignments

| Agent | Milestones | Primary Deliverables |
|---|---|---|
| Backend Engineer | P3-M1, P3-M2 | DeviceAdapter protocol, DeviceRegistry, WebSocketBroker |
| HA Engineer | P3-M1.4, P3-M3, P3-M4 | HA sensor adapter, ESPHome adapter, Bluetooth adapter |
| Frontend Engineer | P3-M5 | WebSocket client, live dashboard, auto-fill |
| QA Engineer | All | Adapter tests, WebSocket tests, integration tests |
| Architect | P3-M4.1, oversight | Bluetooth research, architecture compliance |

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BLE stack unavailable on HA | Medium | High | Detect at startup; disable Bluetooth adapters gracefully |
| ESPHome API changes | Low | Medium | Pin to tested ESPHome version |
| Bluetooth pairing UX poor | High | Medium | Clear error messages; fallback to manual entry |
| WebSocket disconnects on HA restart | Medium | Low | Auto-reconnect with exponential backoff |
| Release validation failure blocks Phase 3 | Unknown | High | Wait for verdict; do NOT proceed without pass |
| HABridgeProtocol migration breaks entity publishing | Low | High | Q1 implemented and tested before P3-M1 begins |

---

## 7. Exit Criteria

Phase 3 is complete when:

1. At least one device adapter is functional end-to-end (HA sensor + ESPHome or Bluetooth)
2. WebSocket endpoint serves real-time device readings at `/api/v1/fertility/ws`
3. Frontend dashboard updates live without manual refresh
4. Device registry is configurable via add-on options in `config.yaml`
5. No new cloud dependencies introduced
6. All tests pass (adapter tests, WebSocket tests, integration tests)
7. Works through HA Ingress proxy

---

## 8. Definition of Done (per milestone)

Each milestone is complete only when:

- [ ] Implementation done
- [ ] Tests written and passing
- [ ] Runtime validated (Docker + HA)
- [ ] Documentation updated
- [ ] Security reviewed (no cloud deps, encrypted where applicable)
- [ ] Graphify updated (nodes + edges)
- [ ] Architect approved

---

## 9. Blocking Gates

| Gate | Blocks | Condition |
|---|---|---|
| Release Engineer PASS | All Phase 3 | Phase 2 RC1 validated |
| Q1 HABridgeProtocol | P3-M1 | Direct import removed, protocol in place |
| ADR-0011/0012 acceptance | All Phase 3 | ADRs accepted (COMPLETE) |
| Milestone N-1 completion | Milestone N | Previous milestone complete + Graphify updated |

---

*Phase 3 begins after: Release validation PASS + Q1 complete + this document finalized.*
