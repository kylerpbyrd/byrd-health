# Phase 4 Work Breakdown Structure

> **Date:** 2026-07-26 | **Author:** Lead Architect / Program Manager  
> **Source:** `docs/architecture/ARCHITECTURE_HEALTH_REPORT.md`  
> **Total work packages:** 31 | **Engineers required:** 5 | **Parallel tracks:** 3

---

## Prerequisites (3 work packages — must complete before Phase 4 feature work)

### PREQ-1: Frontend WebSocket Contract Alignment (3A.8)

| Field | Value |
|---|---|
| **Why it exists** | Contract 6 audit revealed frontend `useWebSocket` types don't match the canonical `WEBSOCKET_PROTOCOL.md`. The `DeviceReading` and `AnalysisComplete` interfaces use ad-hoc shapes that predate the spec. Until aligned, device_reading messages won't parse correctly in the frontend. |
| **Owner** | Frontend Engineer |
| **Est. effort** | 2 hours (S) |
| **Dependencies** | None — `docs/specs/WEBSOCKET_PROTOCOL.md` is the authoritative contract |
| **Validation** | `npm run build` passes; `useWebSocket.ts` types match spec §6.2; DashboardPage and EntryPage callbacks work with canonical payloads |
| **Release impact** | **Blocks Phase 4B** — live dashboard must function before new module dashboards are built. Does NOT block Phase 4A feature work (pregnancy is server-side). |
| **Parallel with** | PREQ-2, PREQ-3, 4A.1, 4A.4, 4A.5, 4A.8, 4A.10 |

**Work steps:**
1. Replace `DeviceReading`/`AnalysisComplete`/`WSMessage` types with `WSEnvelope`/`DeviceReadingPayload`/`AnalysisCompletePayload`
2. Update `ws.onmessage` handler: parse envelope, check version, dispatch by type, ignore unknown types
3. Update `DashboardPage.tsx` `onDeviceReading` callback: `reading.temperature` (not `reading.payload.data.temperature`)
4. Update `EntryPage.tsx` `onDeviceReading` callback: same path fix
5. Remove old dead types. Run `npm run build`.

---

### PREQ-2: Multi-Architecture Docker Builds (TD-003)

| Field | Value |
|---|---|
| **Why it exists** | HA Community Store requires ARM images. `config.yaml` claims `aarch64` support but CI only builds `linux/amd64`. ARM users (Raspberry Pi) cannot run the add-on. |
| **Owner** | DevOps Engineer |
| **Est. effort** | 4 hours (M) |
| **Dependencies** | None — `container-build.yml` already has Buildx configured |
| **Validation** | `container-build.yml` pushes `linux/amd64` and `linux/arm64` images to GHCR. Pull and run on ARM emulation (QEMU) if physical ARM hardware unavailable. |
| **Release impact** | **Blocks Community Store submission.** Does NOT block Phase 4 feature work (dev Docker builds on x86 still work). |
| **Parallel with** | PREQ-1, PREQ-3, 4A.1, 4A.2 |

**Work steps:**
1. Add `linux/arm64` to `platforms` in `container-build.yml`
2. Enable QEMU in CI: `docker/setup-qemu-action@v3`
3. Update `config.yaml` arch list to match what's actually built
4. Test build on PR. Once merged, verify image pulls on ARM.

---

### PREQ-3: C8 Dashboard Indicator Investigation (TD-010)

| Field | Value |
|---|---|
| **Why it exists** | VS-2 validation confirmed WebSocket connects via Ingress (C5 PASS), but the dashboard "Live/Offline" indicator shows "Offline" (C8). Direct `page.evaluate` WS tests succeed; React hook's `isConnected` state may not propagate to UI. This is the Phase 3 flagship feature. |
| **Owner** | Frontend Engineer |
| **Est. effort** | 4 hours (M) |
| **Dependencies** | PREQ-1 (may be related — contract mismatch could cause parsing failures that prevent `isConnected` from transitioning) |
| **Validation** | Dashboard shows "Live" with green dot within 10s of page load when WebSocket connects via Ingress. Verified on live HA instance (VS-2 C5 + C8). |
| **Release impact** | **Blocks Phase 4A milestone** — live dashboard indicator is the Phase 3 flagship feature. |
| **Parallel with** | PREQ-2, 4A.2, 4A.4, 4A.5, 4A.8, 4A.10 |

**Work steps:**
1. Add console logging to `useWebSocket` hook: `ws.onopen` timestamp, `isConnected` state transitions
2. Verify `isConnected` transitions from `false` to `true` after `ws.onopen` fires
3. Check if DashboardPage's re-render is triggered when `isConnected` changes
4. Check for React state batching issues (React 18 automatic batching may suppress re-renders)
5. Check if the green dot conditional (`isConnected ? "bg-green-500" : "bg-red-500"`) is reading stale state
6. Fix root cause. Re-run VS-2 C5+C8 on live HA.

---

## Phase 4A — Platform Hardening & Pregnancy Tracking (11 work packages)

### Concurrent Track 1: Schema & ADR Cleanup (3 packages)

---

#### 4A.1: Schema Consolidation (TD-008)

| Field | Value |
|---|---|
| **Objective** | Eliminate duplicated Pydantic schemas between `data_service/schemas.py` and `web_api/schemas/responses.py`. Make data_service the canonical source. Web API re-exports. |
| **Owner** | Backend Engineer |
| **Complexity** | M — 6 overlapping classes, subtle field differences |
| **Est. effort** | 4 hours |
| **Dependencies** | None |
| **Deliverables** | `data_service/schemas.py` contains all canonical schemas. `web_api/schemas/responses.py` imports and re-exports. All router imports updated. |
| **Completion criteria** | No duplicated class definitions across packages. All tests pass. `ProfileResponse`, `TempResponse`, `SignsResponse`, `SymptomResponse`, `EntryResponse`, `InsightsResponse` defined once. |
| **Verification** | `python -m pytest packages/web_api/tests/ packages/data_service/tests/ -q` — all pass. `git grep "class ProfileResponse"` returns exactly 1 result. |
| **Parallel with** | PREQ-1, PREQ-2, PREQ-3, 4A.2, 4A.4, 4A.5 |

---

#### 4A.8: Error Response Standardization

| Field | Value |
|---|---|
| **Objective** | Standardize all API error responses to `{"detail": "message"}` format with consistent HTTP status codes. |
| **Owner** | Backend Engineer |
| **Complexity** | S — audit, not redesign |
| **Est. effort** | 2 hours |
| **Dependencies** | None (but benefits from 4A.1 being complete to avoid merge conflicts) |
| **Deliverables** | All routers return consistent error shapes. OpenAPI error schema documented. |
| **Completion criteria** | Every `HTTPException` in routers uses consistent format. No raw string errors. |
| **Verification** | Audit all 7 router files for `HTTPException` calls. Run API tests. |
| **Parallel with** | PREQ-1, PREQ-2, PREQ-3, 4A.2, 4A.4, 4A.5 |

---

#### 4A.10: ADR Accuracy Updates

| Field | Value |
|---|---|
| **Objective** | Fix ADR-0011 endpoint mismatch (docs `{id}/read`, impl is `/read`). Fix ADR-0008 encryption claim (HKDF → SHA-256). |
| **Owner** | Architect |
| **Complexity** | S |
| **Est. effort** | 1 hour |
| **Dependencies** | None |
| **Deliverables** | ADR-0011 §2.4 corrected. ADR-0008 §X corrected. |
| **Completion criteria** | ADRs match implementation. |
| **Verification** | Read both ADRs; confirm section matches code. |
| **Parallel with** | All other packages |

---

### Concurrent Track 2: Pregnancy Engine (3 packages)

---

#### 4A.4: Pregnancy Data Model

| Field | Value |
|---|---|
| **Objective** | Add `Pregnancy` SQLAlchemy model to `data_service`. Create Alembic migration. |
| **Owner** | Database Engineer |
| **Complexity** | S — single table |
| **Est. effort** | 2 hours |
| **Dependencies** | 4A.1 (schema consolidation must be done first to avoid merge conflicts on schemas.py) |
| **Deliverables** | `Pregnancy` model in `models.py`. Migration `_002_pregnancy.py`. Repository class. |
| **Completion criteria** | Table creates on migration. `pregnancy_repo.create()` works. FK to `cycles` table enforces referential integrity. |
| **Verification** | `python -m pytest packages/data_service/tests/ -q` — new tests pass. Model appears in test DB. |
| **Parallel with** | PREQ-2, PREQ-3, 4A.5 (engine needs model to exist) |

---

#### 4A.5: Pregnancy Engine

| Field | Value |
|---|---|
| **Objective** | Create `packages/pregnancy_engine/` — pure Python package. Date math: due date = ovulation_date + 266 days, current week = (today - LMP) / 7, trimester = week / 13. |
| **Owner** | Backend Engineer |
| **Complexity** | S — date arithmetic |
| **Est. effort** | 3 hours |
| **Dependencies** | 4A.4 (needs Pydantic models from data_service for I/O contracts) |
| **Deliverables** | `pregnancy_engine` package. `pyproject.toml`. `__init__.py`. `calculator.py`. `models.py`. Tests. |
| **Completion criteria** | `calculate_due_date(ovulation_date)` returns correct date. `calculate_current_week(lmp_date)` returns correct week. Tests cover edge cases (conception date, IVF dates). |
| **Verification** | `python -m pytest packages/pregnancy_engine/tests/ -q` — new tests pass. |
| **Parallel with** | PREQ-2, PREQ-3, 4A.6 (router needs engine) |

---

#### 4A.6: Pregnancy REST Endpoints

| Field | Value |
|---|---|
| **Objective** | Add `routers/pregnancy.py` to web_api. `GET /api/v1/fertility/pregnancy` (current pregnancy data), `POST /api/v1/fertility/pregnancy` (start tracking pregnancy from a cycle). |
| **Owner** | Backend Engineer |
| **Complexity** | S |
| **Est. effort** | 2 hours |
| **Dependencies** | 4A.4 (data model), 4A.5 (engine) |
| **Deliverables** | `routers/pregnancy.py` with 2 endpoints. Response schemas. Tests. |
| **Completion criteria** | `POST` creates pregnancy record, triggers engine compute. `GET` returns current week, trimester, due date, days remaining. |
| **Verification** | `python -m pytest packages/web_api/tests/test_api_pregnancy.py -q` — new tests pass. |
| **Parallel with** | PREQ-3, 4A.7 (frontend needs API) |

---

### Concurrent Track 3: Frontend & Branding (3 packages)

---

#### 4A.2: Branding Assets

| Field | Value |
|---|---|
| **Objective** | Create icon (256x256 PNG), logo, and screenshot for HA Community Store. Update `config.yaml` with `panel_icon`, `panel_admin`, proper descriptions. |
| **Owner** | Documentation Engineer + Frontend Engineer |
| **Complexity** | S |
| **Est. effort** | 2 hours |
| **Dependencies** | None |
| **Deliverables** | `icon.png`, `logo.png` in `repository/byrd_health_fertility/`. Updated `config.yaml`. |
| **Completion criteria** | Icon meets HA Community Store guidelines (256x256, PNG, < 1MB). Config has all required metadata fields. |
| **Verification** | Visual review. `config.yaml` passes `check-yaml` pre-commit hook. |
| **Parallel with** | All packages except 4A.7 |

---

#### 4A.3: OpenAPI Documentation

| Field | Value |
|---|---|
| **Objective** | Add descriptions, examples, and error response schemas to all FastAPI route docstrings. Verify `/docs` renders correctly. |
| **Owner** | Backend Engineer |
| **Complexity** | S |
| **Est. effort** | 2 hours |
| **Dependencies** | 4A.8 (error standardization) — OpenAPI should document the standardized errors |
| **Deliverables** | Every endpoint has `summary`, `description`, `responses={200: ..., 404: ...}` in FastAPI decorator. |
| **Completion criteria** | `GET /docs` shows all endpoints with descriptions. Error codes documented per endpoint. |
| **Verification** | Start server locally, browse `/docs`, verify all endpoints documented. |
| **Parallel with** | PREQ-1, PREQ-2, PREQ-3, 4A.5 |

---

#### 4A.7: Pregnancy Frontend

| Field | Value |
|---|---|
| **Objective** | Pregnancy dashboard page: due date countdown, current week/trimester, week-by-week development info, "Start Tracking" button. |
| **Owner** | Frontend Engineer |
| **Complexity** | M |
| **Est. effort** | 4 hours |
| **Dependencies** | 4A.6 (needs REST API), PREQ-1 (WebSocket types must be canonical) |
| **Deliverables** | `frontend/src/pages/PregnancyPage.tsx`. Route in `App.tsx`. Nav link. |
| **Completion criteria** | Page renders via Ingress. Shows due date, current week, trimester. Start button creates pregnancy from current cycle. |
| **Verification** | Manual test on live HA. `npm run build` succeeds. |
| **Parallel with** | 4A.9 (AI explanation) |

---

#### 4A.9: Cycle Explanation (AI Template)

| Field | Value |
|---|---|
| **Objective** | Generate human-readable explanation of cycle analysis using parameterized templates. Example: "Your coverline is 97.5°F based on the 6 most recent pre-ovulatory temperatures. Ovulation was confirmed on cycle day 15 using the standard 3-day-above-coverline rule." |
| **Owner** | Backend Engineer |
| **Complexity** | S — template engine |
| **Est. effort** | 3 hours |
| **Dependencies** | None (consumes existing `CycleInsights` output) |
| **Deliverables** | `explanation.py` in fertility_engine (or new `ai_engine` package). Template strings with parameterized slots. API endpoint or field on insights response. |
| **Completion criteria** | Explanation renders for any cycle with confirmed ovulation. Fallback text for insufficient data. |
| **Verification** | Unit tests with known cycle data. Verify explanation accuracy against known outputs. |
| **Parallel with** | 4A.3, 4A.6, 4A.7 |

---

### Integration & Validation (1 package)

#### 4A.11: Phase 4A Integration Test & Graphify Update

| Field | Value |
|---|---|
| **Objective** | Run full test suite after all 4A packages complete. Update Graphify with new service (pregnancy_engine), new entity (Pregnancy), new milestone (4A complete). |
| **Owner** | QA Engineer + Graphify Engineer |
| **Complexity** | S |
| **Est. effort** | 1 hour |
| **Dependencies** | ALL 4A.1-4A.10 complete |
| **Deliverables** | Passing test suite. Updated Graphify nodes. |
| **Completion criteria** | 255+ tests pass. Graphify reflects Phase 4A completion. |
| **Verification** | `python -m pytest packages/ -q`. Graphify index audit. |

---

## Phase 4B — Symptoms & Medications (8 work packages)

### Concurrent Track 1: Data & Backend

| ID | Task | Owner | Complexity | Est. | Depends On |
|---|---|---|---|---|---|
| 4B.1 | Symptom catalog data model | Database Engineer | S | 2h | 4A.11 |
| 4B.2 | Medication tracking data model | Database Engineer | S | 2h | 4A.11 |
| 4B.3 | Symptom catalog REST endpoints | Backend Engineer | S | 1h | 4B.1 |
| 4B.4 | Medication REST endpoints | Backend Engineer | S | 2h | 4B.2 |
| 4B.7 | HA entities update (pregnancy + symptom + medication) | HA Engineer | S | 2h | 4B.3, 4B.4 |
| 4B.8 | WebSocket heartbeat message type | Backend Engineer | S | 1h | PREQ-1 |

### Concurrent Track 2: Frontend

| ID | Task | Owner | Complexity | Est. | Depends On |
|---|---|---|---|---|---|
| 4B.5 | Symptom catalog frontend | Frontend Engineer | M | 3h | 4B.3, PREQ-1 |
| 4B.6 | Medication frontend | Frontend Engineer | M | 3h | 4B.4, PREQ-1 |

### Integration

| ID | Task | Owner | Complexity | Est. | Depends On |
|---|---|---|---|---|---|
| 4B.9 | Phase 4B Integration Test & Graphify | QA + Graphify | S | 1h | All 4B |

---

## Phase 4C — Sleep Tracking (5 work packages)

| ID | Task | Owner | Complexity | Est. | Depends On |
|---|---|---|---|---|---|
| 4C.1 | Sleep engine package | Backend Engineer | M | 4h | 4B.9 |
| 4C.2 | Sleep data model | Database Engineer | S | 2h | 4B.9 |
| 4C.3 | Sleep REST endpoints | Backend Engineer | S | 2h | 4C.1, 4C.2 |
| 4C.4 | Sleep frontend | Frontend Engineer | M | 6h | 4C.3, PREQ-1 |
| 4C.5 | Sleep-Fertility cross-module correlation | Backend Engineer | M | 3h | 4C.3 |

---

## Phase 4D — Nutrition Tracking (4 work packages)

| ID | Task | Owner | Complexity | Est. | Depends On |
|---|---|---|---|---|---|
| 4D.1 | Nutrition engine package | Backend Engineer | M | 4h | 4C.5 |
| 4D.2 | Nutrition data model | Database Engineer | M | 3h | 4C.5 |
| 4D.3 | Nutrition REST endpoints | Backend Engineer | M | 3h | 4D.1, 4D.2 |
| 4D.4 | Nutrition frontend | Frontend Engineer | M | 6h | 4D.3, PREQ-1 |

---

## Work Package Summary

| Phase | Packages | Total Est. Hours | Engineers |
|---|---|---|---|
| Prerequisites | 3 | 10h | 2 |
| Phase 4A | 11 | 27h | 5 |
| Phase 4B | 9 | 17h | 5 |
| Phase 4C | 5 | 17h | 3 |
| Phase 4D | 4 | 16h | 3 |
| **Total** | **31** | **87h** | **5** |
