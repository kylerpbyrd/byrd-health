# Phase 3 Execution Plan (Revised)

> **Status:** Authorized | **VS-1:** PASS | **ADRs:** 0011, 0012 Accepted  
> **Date:** 2026-07-26 | **Revision:** 2 (incorporating architecture review)

---

## 1. Authorization

Phase 3 is authorized per the following decisions:

| Decision | Status |
|---|---|
| ADR-0011 — Device Adapter Pattern | Accepted |
| ADR-0012 — WebSocket Architecture | Accepted |
| VS-1 Release Validation | PASS (8/8 checks on live HA) |
| Quick Wins Q1-Q3 | Q1 CLOSED, Q2 DONE, Q3 DONE |

---

## 2. Pre-Flight Checklist

- [x] Release Engineer certifies Phase 2 RC1 (VS-1 PASS)
- [x] Q1: HABridgeProtocol — **CLOSED as Accepted Exception** (see below)
- [x] Q2: Mypy `explicit_package_bases` configured
- [x] Q3: Frontend route-based code-split with `React.lazy` + `Suspense`
- [x] ADR-0006 updated with composition root implementation note
- [ ] `PHASE3_EXECUTION_PLAN.md` (this document — revised and committed)

### Q1 Closure Detail

The `HABridgeProtocol` exists at `packages/web_api/src/web_api/ha_protocol.py`. All routers, dependencies, and business logic use the protocol via `get_ha_bridge()` → `HABridgeProtocol`. The only remaining direct import of concrete `HABridge` is in `app.py:25-26` — the application composition root.

**Decision:** This is an accepted exception. Composition roots are responsible for wiring concrete infrastructure. It does not violate ADR-0006. ADR-0006 §2.3 now includes an Implementation Note documenting this exception.

Q1 is **CLOSED**. No further action required.

---

## 3. Revised Phase Structure

Phase 3 implementation already exists (P3-M1 through P3-M5 code, tests, and WebSocket infrastructure are pre-built). Phase 3 is now a **consolidation and validation phase** — three sub-phases:

```
VS-1 PASS
    │
    ▼
Phase 3-A: Gap Remediation ───── (parallel where possible)
    │
    ▼
Phase 3-B: Integration Validation ─ (runtime on live HA)
    │
    ▼
Phase 3-C: Release Handoff ───── (includes Graphify sync)
```

---

## 4. Phase 3-A: Gap Remediation

**Objective:** Close all pre-existing gaps in the Phase 3 implementation before integration validation.

All tasks in this phase must complete before Phase 3-B begins.

### 4.1 Task Ordering

Tasks are ordered by priority. Within the same priority level, tasks may run in parallel.

| # | Task | Owner | Priority | Dependencies |
|---|---|---|---|---|
| 3A.1 | Remove WebSocket kill switch | Frontend Engineer | 🔴 Critical | None |
| 3A.2 | Integrate device_adapters into root pytest | QA Engineer | 🔴 Critical | None |
| 3A.3 | Run complete repository test suite | QA Engineer | 🔴 Critical | 3A.2 |
| 3A.4 | Fix adapter export issues | Backend Engineer | 🟡 | None |
| 3A.5 | Frontend/API Contract Verification | Frontend Engineer + QA Engineer | 🟡 | None |
| 3A.6 | WebSocket Authentication Architecture Review | Security Engineer | 🟡 | None |

### 4.2 Task Details

#### 3A.1 — Remove WebSocket Kill Switch

**File:** `frontend/src/hooks/useWebSocket.ts:36-40`

The `useWebSocket` hook has a debug kill switch (`window.__ENABLE_WS__`) added in commit `fe0d0a4`. When the kill switch is active (the default), the hook returns `{ isConnected: false, lastMessage: null }` immediately without opening any connection. This renders P3-M5 (Frontend Real-Time) non-functional for end users.

**Action:** Remove the kill switch guard entirely. The hook must attempt a WebSocket connection on mount by default. The connection will succeed when running under HA Ingress (which proxies WebSocket upgrades) and fail gracefully otherwise.

**Deliverable:** `useWebSocket.ts` connects on mount without requiring manual browser console intervention.

**Acceptance:**
- [ ] Dashboard "Live" indicator connects through HA Ingress
- [ ] Hook does not error when running outside HA Ingress (standalone dev)
- [ ] Auto-reconnect behavior preserved (exponential backoff, 1s → 30s cap)

---

#### 3A.2 — Integrate device_adapters into Root Pytest Configuration

**File:** `pyproject.toml` lines 92-104

The `device_adapters` package has 53 passing tests but is excluded from the root test suite. Running `pytest` from the repository root skips all device adapter tests.

**Action:** Add `"packages/device_adapters"` to `testpaths` and `"packages/device_adapters/src"` to `pythonpath` in root `pyproject.toml`.

**Deliverable:** `pytest --co` from repo root reports all package tests including device_adapters.

**Acceptance:**
- [ ] `testpaths` includes all 5 packages
- [ ] `pythonpath` includes all 5 package `src/` directories
- [ ] `pytest` from root discovers device_adapters tests
- [ ] No import conflicts introduced (device_adapters depends on ha_bridge)

---

#### 3A.3 — Run Complete Repository Test Suite

**Dependency:** 3A.2

Run `python -m pytest` from repository root. All tests must pass across all packages:

| Package | Expected Tests |
|---|---|
| `fertility_engine` | (existing) |
| `data_service` | (existing) |
| `web_api` | (existing + WebSocket + devices) |
| `ha_bridge` | (existing) |
| `device_adapters` | 53 (protocol, registry, bluetooth, esphome, ha_sensor) |
| **Total** | ~315+ |

**Deliverable:** Passing test report. Any failures documented and remediated.

**Acceptance:**
- [ ] Zero test failures
- [ ] Zero unhandled warnings
- [ ] CI-equivalent run (same flags as GitHub Actions would use)

---

#### 3A.4 — Fix Adapter Export Issues

**File:** `packages/device_adapters/src/device_adapters/adapters/__init__.py`

`ESPHomeAdapter` is not exported from the adapters package init. Only `BluetoothAdapter` and `HASensorAdapter` are exported. `ESPHomeAdapter` exists and has 14 passing tests but is invisible to consumers.

**Action:** Add `from device_adapters.adapters.esphome import ESPHomeAdapter` and include it in `__all__`.

**Deliverable:** All three concrete adapters exported from `adapters/__init__.py`.

**Acceptance:**
- [ ] `from device_adapters.adapters import ESPHomeAdapter` works
- [ ] `from device_adapters.adapters import BluetoothAdapter` still works
- [ ] `from device_adapters.adapters import HASensorAdapter` still works

---

#### 3A.5 — Frontend/API Contract Verification

**Objective:** Verify that every frontend request and response shape matches the backend API contract. Document any drift.

**Scope:**

| Contract | Frontend | Backend | File(s) |
|---|---|---|---|
| EntryForm payload | `EntryForm.tsx` → `POST /entries/` | `EntryRequest` in `routers/entries.py` | `frontend/src/components/EntryForm.tsx`, `frontend/src/lib/api.ts:173-207` |
| Symptoms payload | Embedded in entry `symptoms[]` | `SymptomItem` in `routers/entries.py` | `frontend/src/types/fertility.ts:126-132` |
| Create Cycle payload | `createCycle()` → `POST /cycles/` | `NewCycleRequest` in `routers/cycles.py` | `frontend/src/lib/api.ts:285-293` |
| Dashboard response | `DashboardData` in `types/fertility.ts` | `InsightsResponse` + `CycleDetailResponse` | `frontend/src/types/fertility.ts:71-85`, `responses.py:154-170` |
| Calendar response | `CalendarResponse` in `types/fertility.ts` | `CalendarResponse` in `responses.py` | `frontend/src/types/fertility.ts:243-251`, `responses.py:194-226` |
| WebSocket payload | `WSMessage` union in `useWebSocket.ts` | `device_reading` / `analysis_complete` | `frontend/src/hooks/useWebSocket.ts:3-21`, `routers/devices.py:29-42` |

**Action:** For each contract pair, verify:
1. Field names match (case-sensitive)
2. Field types are compatible (string/number/boolean/nullable)
3. Required vs. optional fields are consistent
4. No frontend-sent fields are silently dropped by the backend
5. No backend-returned fields are unused by the frontend

**Deliverable:** Contract audit document or summary table with findings. Discrepancies flagged for remediation.

**Acceptance:**
- [ ] All 6 contracts verified
- [ ] Discrepancies documented (none expected based on preliminary analysis)
- [ ] Any breaking mismatches fixed before Phase 3-B

---

#### 3A.6 — WebSocket Authentication Architecture Review

**Objective:** Determine the WebSocket endpoint's security posture and produce a documented trust model.

**Questions to answer:**

1. Can `/api/v1/fertility/ws` be reached directly on port 8000 when running standalone (`docker run -p 8000:8000`)?
2. Does HA Ingress proxy WebSocket upgrade requests? (ADR-0012 §2.5 asserts yes — verify against actual HA Supervisor behavior)
3. Is the `ingress_session` cookie validated for WebSocket connections, or do WebSocket upgrades bypass cookie-based auth?
4. What happens in standalone mode (no HA Ingress) — should the WebSocket endpoint require explicit token authentication?
5. Is additional token validation required, or is the current trust model (HA Ingress provides auth, standalone is development-only) sufficient?
6. For future ByrdOS multi-user deployment, what auth changes would be needed?

**Action:** Produce a documented trust model with recommendations. Do NOT implement changes until the review is complete and approved.

**Deliverable:** WebSocket trust model document (may be added to ADR-0012 as an implementation note, or as a standalone security review doc).

**Acceptance:**
- [ ] All 6 questions answered with evidence
- [ ] Trust model documented
- [ ] Recommendations captured (for Phase 4 or future ADR)
- [ ] No auth changes implemented unless explicitly approved

---

## 5. Phase 3-B: Integration Validation

**Objective:** Validate the complete Phase 3 implementation on the live Home Assistant instance at `192.168.1.44:8123`.

**Prerequisite:** All Phase 3-A tasks complete.

### 5.1 VS-2 Runtime Validation Suite

**File:** `tools/validate-vs2.ts` (extends VS-1 with Phase 3 scenarios)

VS-2 validates more than a successful WebSocket connection. It must exercise the complete real-time pipeline under realistic conditions.

**Base Scenarios (carried forward from VS-1):**

| Check | Description |
|---|---|
| VS2-C1 | Dashboard loads via Ingress |
| VS2-C2 | All nav pages render |
| VS2-C3 | HA Core API reachable |
| VS2-C4 | Byrd Health entities published |

**WebSocket Scenarios (new):**

| Check | Description | Runtime Evidence |
|---|---|---|
| VS2-C5 | WebSocket upgrade succeeds via Ingress | Console log: `isConnected` → `true` |
| VS2-C6 | Device reading broadcast reaches frontend | Toast notification appears with temperature |
| VS2-C7 | Entry form auto-fills from device reading | Temperature field pre-populated with device value |
| VS2-C8 | Live dashboard indicator shows "Live" | Green dot visible when WebSocket connected |

**Resilience Scenarios (new):**

| Check | Description | Evidence |
|---|---|---|
| VS2-C9 | Browser refresh reconnect | After page reload, WebSocket reconnects within 10s |
| VS2-C10 | Home Assistant restart reconnect | After HA restart (or add-on restart), hook reconnects |
| VS2-C11 | Temporary network interruption | After brief disconnect, hook reconnects with backoff |
| VS2-C12 | Multiple browser tabs | Two tabs both receive broadcasts; no interference |
| VS2-C13 | Stale WebSocket cleanup | Broker removes dead connections (verify `connection_count`) |
| VS2-C14 | Graceful shutdown | No errors on add-on stop; connections closed cleanly |

**Validation approach:** Playwright test suite run against the live HA instance. Resilience scenarios may require manual orchestration (HA restart, network interruption) with automated assertions.

### 5.2 End-to-End Pipeline Validation

**Requirement:** At least one complete pipeline must function end-to-end:

```
HA Sensor Entity
    │
    ▼
HASensorAdapter.read_temperature()
    │
    ▼
DeviceRegistry.read_all()
    │
    ▼
POST /api/v1/fertility/entries/ (persist reading)
    │
    ▼
fertility_engine.analyze_cycle() (re-analyze)
    │
    ▼
ha_bridge.publish_insights() (HA entity update)
    │
    ▼
WebSocketBroker.broadcast({ type: "analysis_complete" })
    │
    ▼
Frontend useWebSocket.onAnalysisComplete → queryClient.invalidateQueries
    │
    ▼
Dashboard re-renders with updated BBT chart and phase
    │
    ▼
Toast notification visible
```

**Acceptance:**
- [ ] All nodes in the pipeline produce the expected output
- [ ] Pipeline completes in under 5 seconds (from sensor read to dashboard refresh)
- [ ] No manual intervention required between pipeline stages
- [ ] Pipeline works through HA Ingress (no direct API access needed)

---

## 6. Phase 3-C: Release Handoff

**Objective:** Formal handoff to Release Engineer with complete evidence package.

**Prerequisite:** Phase 3-B complete (VS-2 PASS).

### 6.1 Handoff Tasks

| # | Task | Owner |
|---|---|---|
| 3C.1 | Hand off Phase 3 to Release Engineer (VS-2 results, pipeline evidence, contract audit, WS trust model) | Architect |
| 3C.2 | Release Engineer runs VS-2 validation on live HA, returns pass/fail verdict | Release Engineer |
| 3C.3 | On PASS: Update CHANGELOG, tag release candidate | Release Engineer |
| 3C.4 | On PASS: Sync Graphify to reflect Phase 3 completion | Graphify Engineer + Architect |
| 3C.5 | On FAIL: Schedule remediation, do NOT advance to Phase 4 | Architect |

### 6.2 Graphify Synchronization (Phase 3-C Only)

Graphify synchronization is deferred to the Release Handoff phase. It must not delay engineering or validation work.

**Required updates:**

1. **Service nodes:** Update all service statuses to reflect actual implementation state:
   - `fertility-engine` → `verified`
   - `data-service` → `verified`
   - `web-api` → `verified`
   - `web-frontend` → `verified`
   - `ha-bridge` → `verified`
   - `device-adapters` → `verified`

2. **Phase nodes:** Update phase statuses:
   - `phase-1` → `complete` (currently incorrectly `in_progress`)
   - `phase-2` → `complete` (correct)
   - `phase-3` → `complete`

3. **ADR nodes:** Create node files for ADRs 0001-0013 that currently exist only as index entries.

4. **Agent nodes:** Create node files for all registered agents (11 entries, currently 0 files).

5. **Concept/Integration nodes:** Create node files for registered concepts and integrations.

6. **Edges:** Add Phase 3 governance and dependency edges (device-adapters ↔ phase-3, frontend → WebSocket, etc.).

7. **Index:** Update `last_updated` timestamp, verify all registered nodes have backing files.

**Acceptance:**
- [ ] `index.json` registered node count matches actual node file count (± allowable omissions)
- [ ] All service nodes reflect actual implementation status
- [ ] Phase statuses are logically consistent (1→complete, 2→complete, 3→complete)
- [ ] All ADR nodes (0011, 0012 at minimum) have complete node files
- [ ] New edges for device adapters, WebSocket, and live dashboard exist

---

## 7. Exit Criteria

Phase 3 is complete when:

1. **Pipeline:** At least one complete end-to-end device pipeline (sensor → adapter → registry → persistence → analysis → HA publication → WebSocket broadcast → dashboard refresh → notification) functions successfully.

2. **WebSocket:** Endpoint at `/api/v1/fertility/ws` serves real-time messages through HA Ingress without manual configuration.

3. **Frontend:** Dashboard updates live via WebSocket (no manual refresh required). Live/Offline indicator reflects actual connection state.

4. **Tests:** Complete test suite passes from repository root (all 5 packages, ~315+ tests).

5. **Contracts:** Frontend/API contract audit complete; no unaddressed drift.

6. **Security:** WebSocket trust model documented; no unauthenticated access path in production configuration.

7. **Privacy:** No new cloud dependencies introduced. All processing remains local.

8. **VS-2:** Release Engineer certifies VS-2 PASS on live HA instance.

9. **Graphify:** Knowledge graph synchronized to reflect Phase 3 completion.

---

## 8. Agent Assignments

| Agent | Phase | Tasks |
|---|---|---|
| **Frontend Engineer** | 3A, 3B | 3A.1 (kill switch), 3A.5 (contract audit — frontend side), 3B (frontend validation) |
| **QA Engineer** | 3A, 3B | 3A.2 (pytest config), 3A.3 (test suite), 3A.5 (contract audit — API side), 3B (VS-2 suite) |
| **Backend Engineer** | 3A | 3A.4 (adapter exports) |
| **Security Engineer** | 3A | 3A.6 (WS auth review) |
| **Release Engineer** | 3C | VS-2 validation, release certification |
| **Graphify Engineer** | 3C | Graphify synchronization |
| **Architect** | All | Oversight, ADR updates, milestone handoff |

---

## 9. Blocking Gates

| Gate | Blocks | Condition |
|---|---|---|
| VS-1 PASS | Phase 3 | Phase 2 RC1 validated ✅ |
| ADR-0011/0012 | Phase 3 | ADRs accepted ✅ |
| Q1-Q3 | Phase 3-B | Quick wins closed ✅ |
| Phase 3-A complete | Phase 3-B | All 6 gap remediation tasks done |
| VS-2 PASS | Phase 3-C | Release Engineer certifies runtime validation |
| Phase 3-C complete | Phase 4 | Release handoff + Graphify sync complete |

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Kill switch removal exposes WebSocket Ingress incompatibility | Low | Medium | Rollback to kill switch with config-based toggle; debug Ingress passthrough |
| Contract audit reveals breaking mismatches | Low | High | Fix mismatches in 3A.5 before 3B begins |
| WebSocket auth review requires immediate implementation | Low | High | Document findings; implement only if unauthenticated access to health data is possible in production |
| VS-2 resilience scenarios unreliable over local network | Medium | Medium | Manual orchestration + relaxed timing assertions |
| Graphify sync reveals inventory gaps needing new node files | High | Low | Accept incremental sync; create nodes for known entities, defer unknown to Phase 4 |
| Device pipeline has timing-dependent failures (analysis slow, entity publish delayed) | Medium | Medium | Measure pipeline latency; add wait tolerances to VS-2 assertions |

---

## 11. Definition of Done (per sub-phase)

Each sub-phase is complete only when:

- [ ] All tasks in the sub-phase complete
- [ ] Acceptance criteria met for each task
- [ ] Blocking gate condition satisfied before next sub-phase
- [ ] Architect review complete

---

*Phase 3-A begins immediately upon this plan being committed. No implementation work begins until plan is committed and approved.*
