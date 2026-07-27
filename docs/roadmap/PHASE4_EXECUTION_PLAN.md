# Phase 4 Execution Plan

> **Status:** Authorized (conditional) | **Date:** 2026-07-26  
> **Prerequisites:** 3A.8, TD-003, TD-010  
> **Architecture Report:** `docs/architecture/ARCHITECTURE_HEALTH_REPORT.md`

---

## Authorization

Phase 4 is authorized conditional on completion of 3 prerequisites (see §2).

| Decision | Status |
|---|---|
| Phase 3 Complete | ✅ (VS-2: 13/14 pass, 0 fail) |
| Phase 3.5 Maintenance Complete | ✅ (14 debt items resolved) |
| Architecture Health Report | ✅ (82/100, GO recommendation) |
| ADR-0007 AI/Prediction | Accepted (Layer 2 unimplemented) |
| ADR-0013 Container Distribution | Accepted (GHCR publishing not built) |

---

## Phase 4 Vision

Phase 4 transforms Byrd Health from a **fertility tracker** into a **health platform**. The fertility module remains the flagship, but the architecture opens to support pregnancy tracking, symptom catalogs, sleep, nutrition, medications, and wearable data sources.

All new modules follow the proven `{module}_engine` + `data_service` + `web_api router` + `frontend pages` pattern. The modular monolith stays intact — no microservices.

---

## Prerequisites (must complete before Phase 4 feature work)

| # | Item | Owner | Est. | Blocks |
|---|---|---|---|---|
| P1 | **3A.8 — Frontend WebSocket contract alignment.** Update `useWebSocket.ts` types to match canonical `WEBSOCKET_PROTOCOL.md`. Remove dead protocol definitions. Update DashboardPage and EntryPage callbacks. | Frontend Engineer | 2 hrs | Phase 4B (live dashboard is prerequisite for new module dashboards) |
| P2 | **TD-003 — Multi-arch Docker builds.** Add `linux/arm64` to `container-build.yml` platforms. Test on ARM emulation. | DevOps Engineer | 4 hrs | Community Store submission |
| P3 | **TD-010 — C8 dashboard indicator.** Investigate why `isConnected` shows Offline despite WebSocket connecting. Fix propagation of `useWebSocket` state to UI. | Frontend Engineer | 4 hrs | Phase 4A (live indicator is Phase 3 flagship) |

---

## Phase 4A — Platform Hardening & Pregnancy Tracking

| # | Task | Owner | Est. |
|---|---|---|---|
| 4A.1 | **Schema consolidation (TD-008).** Move canonical schemas to `data_service/schemas.py`. Make `web_api/schemas/responses.py` re-export from data_service. Remove duplicated class definitions. Update imports across all routers. | Backend Engineer | 4 hrs |
| 4A.2 | **Branding assets.** Create icon (256x256), logo, screenshot for HA Community Store. Add `panel_icon`, `panel_admin` to `config.yaml`. | Docs/Frontend | 2 hrs |
| 4A.3 | **OpenAPI documentation.** Add descriptions, examples, error codes to FastAPI route docstrings. Verify `/docs` renders correctly. | Backend Engineer | 2 hrs |
| 4A.4 | **Pregnancy tracking data model.** Add `Pregnancy` table to data_service. Alembic migration. | Database Engineer | 2 hrs |
| 4A.5 | **Pregnancy tracking engine.** Date math (due date, current week, trimester). New `pregnancy_engine` package. | Backend Engineer | 3 hrs |
| 4A.6 | **Pregnancy REST endpoints.** `GET/POST /api/v1/fertility/pregnancy`. | Backend Engineer | 2 hrs |
| 4A.7 | **Pregnancy frontend.** Pregnancy dashboard, week-by-week view, due date countdown. | Frontend Engineer | 4 hrs |
| 4A.8 | **Error response standardization.** Consistent `{"detail": "..."}` with proper HTTP codes across all routers. | Backend Engineer | 2 hrs |
| 4A.9 | **Cycle explanation (AI template).** Generate human-readable explanation of cycle analysis. Template-based initially. | Backend Engineer | 3 hrs |
| 4A.10 | **ADRs update.** Fix ADR-0011 endpoint mismatch. Fix ADR-0008 encryption claim (HKDF → SHA-256). | Architect | 1 hr |

**Total est.:** ~25 hrs. **Target:** 2 weeks.

---

## Phase 4B — Symptoms & Medications

| # | Task | Owner | Est. |
|---|---|---|---|
| 4B.1 | **Symptom catalog data model.** `SymptomCatalog` table. Seed with common symptoms. | Database Engineer | 2 hrs |
| 4B.2 | **Medication tracking model.** `Medication` table. | Database Engineer | 2 hrs |
| 4B.3 | **Symptom catalog REST.** `GET /api/v1/fertility/symptoms/catalog`. | Backend Engineer | 1 hr |
| 4B.4 | **Medication REST.** `GET/POST /api/v1/fertility/medications`. | Backend Engineer | 2 hrs |
| 4B.5 | **Symptom catalog frontend.** Structured symptom picker replacing free-text input. | Frontend Engineer | 3 hrs |
| 4B.6 | **Medication frontend.** Medication log with schedule tracking. | Frontend Engineer | 3 hrs |
| 4B.7 | **EEA update.** Add pregnancy+symptom+medication entities to HA Bridge. | HA Engineer | 2 hrs |
| 4B.8 | **WebSocket heartbeat.** Add `heartbeat` message type per protocol spec. | Backend Engineer | 1 hr |

**Total est.:** ~16 hrs. **Target:** 2 weeks.

---

## Phase 4C — Sleep Tracking

| # | Task | Owner | Est. |
|---|---|---|---|
| 4C.1 | **Sleep engine.** `sleep_engine` package. Sleep scoring, debt calculation. | Backend Engineer | 4 hrs |
| 4C.2 | **Sleep data model.** `SleepSession` table. | Database Engineer | 2 hrs |
| 4C.3 | **Sleep REST.** `GET/POST /api/v1/fertility/sleep`. | Backend Engineer | 2 hrs |
| 4C.4 | **Sleep frontend.** Sleep chart, weekly trends, cycle correlation view. | Frontend Engineer | 6 hrs |
| 4C.5 | **Sleep ← Fertility correlation.** Cross-module insight: sleep quality by cycle phase. | Backend Engineer | 3 hrs |

**Total est.:** ~17 hrs. **Target:** 2 weeks.

---

## Phase 4D — Nutrition Tracking

| # | Task | Owner | Est. |
|---|---|---|---|
| 4D.1 | **Nutrition engine.** `nutrition_engine` package. Macro calculation. | Backend Engineer | 4 hrs |
| 4D.2 | **Nutrition data model.** `FoodItem`, `Meal`, `MealItem` tables. | Database Engineer | 3 hrs |
| 4D.3 | **Nutrition REST.** `GET/POST /api/v1/fertility/nutrition`. | Backend Engineer | 3 hrs |
| 4D.4 | **Nutrition frontend.** Meal logger, macro dashboard. | Frontend Engineer | 6 hrs |

**Total est.:** ~16 hrs. **Target:** 2 weeks.

---

## Phase 4 Exit Criteria

| # | Criterion |
|---|---|
| 1 | At least Phase 4A (Pregnancy) functional end-to-end |
| 2 | Schema consolidation complete — no duplicated Pydantic models across packages |
| 3 | HA Community Store submission package ready (branding + multi-arch + docs) |
| 4 | OpenAPI docs accurate and complete |
| 5 | All 3 prerequisites (3A.8, TD-003, TD-010) resolved |
| 6 | 255+ tests pass; coverage ≥ 80% |
| 7 | No new circular dependencies or boundary violations |
| 8 | Graphify updated to reflect Phase 4 state |

---

## Agent Assignments

| Agent | Phase |
|---|---|
| Backend Engineer | 4A.4-4A.6, 4A.8-4A.10, 4B.3-4B.4, 4B.8, 4C.1-4C.3, 4C.5, 4D.1-4D.3 |
| Frontend Engineer | 4A.2, 4A.7, 4B.5-4B.6, 4C.4, 4D.4, Prerequisites P1+P3 |
| Database Engineer | 4A.4, 4B.1-4B.2, 4C.2, 4D.2 |
| HA Engineer | 4B.7 |
| DevOps Engineer | Prerequisite P2 |
| Architect | 4A.1 (oversight), 4A.10, Graphify, milestone handoff |

---

## Deferred to Phase 5

| Item | Phase |
|---|---|
| TD-001 Pin Docker base | Phase 5 |
| TD-002 Multi-stage Docker | Phase 5 |
| TD-004 Coverage reporting in CI | Phase 5 |
| TD-005 pip-audit dependency scanning | Phase 5 |
| TD-015 Timing-dependent test fixes | Phase 5 |
| Wearable adapters (Apple Health, Google Fit, Garmin, Fitbit, Oura) | Phase 5A |
| AI: prediction confidence, symptom correlation, anomaly detection | Phase 5A |
| AI: natural language logging | ByrdOS phase |
| Standalone production auth (OAuth2/JWT) | Phase 5B |
| Multi-user data model | Phase 5B |
| PostgreSQL production support | Phase 5B |
| ByrdOSBridge (HA Bridge replacement) | ByrdOS migration |
