# Architecture Health Report

> **Date:** 2026-07-26 | **Author:** Lead Architect  
> **Scope:** 6–12 month architectural assessment  
> **Phase 4 Recommendation:** GO — conditional on completion of deferred 3.5 items

---

## Executive Summary

Byrd Health has a **sound architecture**. Package boundaries are correctly enforced, dependency flow is unidirectional, and the service-oriented design maps cleanly to the three deployment targets: Home Assistant add-on, standalone Docker, and future ByrdOS module.

The architecture scores **82/100** on maturity. Two structural issues require attention before the platform can support additional health modules: schema duplication across packages and a WebSocket contract drift that affects the live dashboard.

Phase 4 is recommended with **three prerequisites**: WebSocket contract alignment (3A.8), multi-arch Docker builds (TD-003), and the C8 dashboard indicator fix (TD-010).

---

## Repository Health Score: 82/100 (up from 78)

| Category | Previous | Current | Change |
|---|---|---|---|
| Architecture Compliance | 10/10 | 10/10 | — |
| Package Boundaries | 10/10 | 10/10 | — |
| Test Quality | 8/10 | 9/10 | +1 (dead tests removed, low-value tests fixed) |
| Documentation Accuracy | 7/10 | 9/10 | +2 (broken refs fixed, stale docs archived) |
| Graphify Accuracy | 7/10 | 10/10 | +3 (18 nodes created, 5 entities fixed) |
| CI/CD Completeness | 6/10 | 7/10 | +1 (mypy aligned, broken eslint removed) |
| Dependency Health | 7/10 | 8/10 | +1 (unused deps removed, explicit ha-bridge dep) |
| Code Cleanliness | 7/10 | 9/10 | +2 (dead code removed, artifacts cleaned) |

---

## Architecture Maturity Score: 82/100

| Dimension | Score | Notes |
|---|---|---|
| **Separation of concerns** | 9/10 | Each package has a single, clear responsibility. Minor: IngressMiddleware duplication intentional but suboptimal. |
| **Dependency direction** | 10/10 | Zero circular dependencies. All flows unidirectional: frontend → web_api → engines/data/adapters. |
| **Interface contracts** | 8/10 | HABridgeProtocol clean. DeviceAdapter Protocol well-defined. WebSocket protocol versioned. Minor: REST schemas duplicated across packages. |
| **Testability** | 8/10 | Each package independently testable. 255 tests. Minor: no coverage enforcement, no property-based tests. |
| **Deployability** | 7/10 | Docker build works. HA add-on works. Minor: no multi-arch, unpinned base image, no standalone auth. |
| **Observability** | 5/10 | Health endpoint exists. No structured logging, no metrics, no tracing. |
| **Security** | 7/10 | AES-256-GCM encryption. HA Ingress auth. Minor: HKDF not used, no dependency scanning, no non-root user. |
| **Extensibility** | 8/10 | Adapter pattern for devices. Protocol pattern for bridges. Engine pattern for algorithms. DB-agnostic SQLAlchemy. |
| **Documentation** | 9/10 | 13 ADRs, architecture doc, protocol spec, developer guide. All accurate after 3.5 cleanup. |
| **ByrdOS readiness** | 7/10 | Engine and data service are fully portable. Web API is framework-portable. HA Bridge must be swapped. Auth model needs redesign for multi-user. |

---

## 1. Package Boundaries — Assessment

### Current State: **Excellent**

All six packages have clear, enforced boundaries:

```
frontend ──(HTTP/WS)──> web_api ──> fertility_engine     (algorithm)
                                  ──> data_service        (persistence)
                                  ──> device_adapters ──> ha_bridge    (HA integration)
                                  ──> ha_bridge
```

**Zero circular dependencies.** Zero import violations. The architecture follows ADR-0001 and ADR-0006 precisely.

### Single Responsibility

| Package | Responsibility | Violations |
|---|---|---|
| `fertility_engine` | Sympto-thermal algorithms | None — pure Python, zero framework deps |
| `data_service` | SQLAlchemy models, repos, encryption, migrations | None — zero cross-package imports |
| `ha_bridge` | HA entity publishing, sensor polling, notifications | None — fully self-contained |
| `device_adapters` | Pluggable device integration | None — only imports ha_bridge (allowed) |
| `web_api` | HTTP/WS gateway, orchestration | Minor: imports concrete HABridge (composition root — accepted exception) |
| `frontend` | React SPA UI | None — only HTTP/WS to web_api |

### Opportunities to Simplify

1. **Schema duplication (TD-008):** `data_service/schemas.py` and `web_api/schemas/responses.py` have 6 overlapping Pydantic models. The web_api should re-export data_service schemas rather than redefine them. This eliminates drift risk.

2. **IngressMiddleware duplication (TD-007):** Both `ha_bridge/ingress.py` and `web_api/ingress.py` implement the same ASGI middleware. Extraction to a shared utility package is architecturally cleaner than the current intentional duplication — but this requires careful handling of the ADR-0006 isolation boundary.

---

## 2. ByrdOS Readiness — Assessment

### Current Readiness: **70%**

| Component | Portability | Notes |
|---|---|---|
| **Fertility Engine** | 100% portable | Zero framework dependencies. Pure Python algorithms. Directly reusable. |
| **Data Service** | 95% portable | SQLAlchemy 2.0 abstracts database. Adding PostgreSQL requires only a connection string change + Alembic migration verification. Encryption module is standalone. |
| **Web API** | 80% portable | FastAPI + Uvicorn are deployment-agnostic. Auth currently depends on HA Ingress — must be replaced with OAuth2/JWT for ByrdOS. CORS config needs production hardening. |
| **HA Bridge** | 0% portable (by design) | Must be **replaced** for ByrdOS. The `HABridgeProtocol` abstraction means this is additive — a `ByrdOSBridge` implementing the same protocol swaps in without touching core code. |
| **Device Adapters** | 30% portable | HASensorAdapter and ESPHomeAdapter use `HAClient` from ha_bridge — HA-specific. BluetoothAdapter uses `bleak` — portable. ByrdOS needs non-HA adapter implementations. |
| **Frontend** | 100% portable | React SPA. Vite build produces static assets. Deployable anywhere. Ingress path resolution (`window.__INGRESS_PATH__`) is environment-agnostic. |

### Required Work for ByrdOS

1. **Authentication layer** — Replace HA Ingress auth with OAuth2/JWT (P1, Phase 4-5)
2. **Multi-user data model** — Add `user_accounts` table; scope profiles to users (P1, Phase 4-5)
3. **ByrdOSBridge** — New bridge implementation replacing HA entity publishing with ByrdOS service bus (P2, Phase 5)
4. **PostgreSQL validation** — Test Alembic migrations against PostgreSQL (P2, Phase 4)
5. **Message queue** — Replace in-memory WebSocketBroker with Redis/RabbitMQ for multi-process (P2, ByrdOS phase)

---

## 3. Home Assistant Readiness — Assessment

### Current Readiness: **85%**

| Requirement | Status | Gap |
|---|---|---|
| Add-on packaging | ✅ `config.yaml`, `Dockerfile`, `run.sh` | Multi-arch builds (TD-003) |
| Entity publishing | ✅ 9 entities per profile | `unique_id` on conditional entities (RELEASE_STATUS risk) |
| Ingress support | ✅ ASGI middleware | — |
| Lovelace card | ✅ `ha-card.js` built | Not yet registered automatically (Phase 3 item) |
| Notifications | ✅ 5 types with config toggles | Notification IDs not per-profile (RELEASE_STATUS risk) |
| Sensor polling | ✅ HASensorAdapter | — |
| bashio config | ✅ 8 options in `run.sh` | — |
| OCI distribution | ✅ GHCR image per ADR-0013 | CI push workflow not built |
| **Branding** | ❌ | No icon, no logo, no metadata screenshot |
| **Translations** | ❌ | No i18n infrastructure |
| **Documentation** | ⚠️ | User guide exists, no in-app help |
| **Community Store compliance** | ⚠️ | ~60% — meets technical requirements, missing branding + translations |

### Community Store Submission Prerequisites

1. Brand assets (icon 256x256, logo, screenshots) — P2
2. `README.md` formatted per HA Community Store guidelines — P2
3. Release tagging (semver) in CI — P1
4. Multi-arch images (amd64 + arm64 minimum) — P1
5. `config.yaml` with `panel_icon`, `panel_admin`, proper descriptions — P2

---

## 4. Standalone Deployment — Recommendation

### Recommendation: **Development Only for Phase 4. Production in Phase 5.**

**Rationale:**

1. **No authentication** — The WebSocket endpoint and REST API are completely unauthenticated in standalone mode. This is unacceptable for a health data platform.

2. **HA Ingress provides production auth for free** — The HA Supervisor's proxy handles authentication, session management, and TLS termination. Replicating this in standalone requires significant security engineering (OAuth2, token management, HTTPS).

3. **Development works today** — `docker run -p 8000:8000` provides a fully functional local instance for testing and development. This is the correct posture for Phase 4.

4. **Phase 5 standalone** — When ByrdOS multi-user auth is implemented, standalone production becomes a natural byproduct. The same JWT/OAuth2 layer serves both.

**Do not remove standalone mode.** It is valuable for development and testing. Document it as "development only" in the README and USER_GUIDE.

---

## 5. Future Modules — Architectural Readiness

### Current Architecture Supports: **Modular Monolith**

Each new health module follows a consistent pattern:

```
packages/{module}_engine/     — Pure algorithms (no framework deps)
packages/{module}_data/       — Subclass of data_service or standalone
web_api/routers/{module}.py   — REST endpoints
frontend/src/pages/{Module}/  — UI components
```

This pattern is proven by `fertility_engine` + `data_service` + fertility routers + fertility pages.

### Module Roadmap

| Phase | Module | Algorithm Complexity | Data Model Complexity | Architecture Impact |
|---|---|---|---|---|
| **4A** | Pregnancy Tracking | Low — date math, week calculation | Low — single entity | **Extension of fertility** (same cycle model, new endpoint) |
| **4B** | Symptoms & Medications | Medium — catalog, scheduling | Medium — catalog tables | New `symptom_catalog` package + `medication_engine` |
| **4C** | Sleep Tracking | Medium — sleep stages, scoring | Medium — time-series data | New `sleep_engine` + `sleep_data` packages |
| **4D** | Nutrition Tracking | High — macro calculation, meal planning | High — food database | New `nutrition_engine` + `nutrition_data`. May require external food DB (offline copy). |
| **5A** | Wearable Integration | Low — API clients | Low — data mapping | New adapters under `device_adapters`. Apple Health, Google Fit, Garmin, Fitbit. |
| **5B** | AI Integration | High — ML models | Low — predictions table | New `ai_engine` package. Depends on fertility/nutrition/sleep data. |

### Architectural Changes Required Before Module Expansion

1. **Schema consolidation (TD-008)** — Fix the data_service/web_api schema duplication before adding new modules. New modules should define schemas in ONE place: `data_service`.

2. **Router pattern** — Standardize the FastAPI router pattern. Currently each router has slightly different conventions for error handling, dependency injection, and response models.

3. **Frontend code organization** — Consider a `packages/frontend/` pattern (like backend packages) or keep the monolithic `frontend/`. The monolith is simpler for Phase 4; split when module count exceeds 3.

---

## 6. AI Readiness — Design Only

### Architecture is AI-ready

The ADR-0007 two-layer design (rules engine + model engine) is correctly implemented:

- **Layer 1 (rules):** Fully built. `fertility_engine/` computes coverline, ovulation, fertile window deterministically.
- **Layer 2 (models):** `PredictionModel` Protocol defined but unimplemented. This is the correct insertion point for ML.

### Integration Points (do not implement — design only)

1. **Cycle Explanation** — NLP-generated paragraph explaining why the algorithm reached its conclusion. Consumes `CycleInsights` output. Uses templated explanation with confidence scores. Runs client-side or server-side. No training data required initially — template-based with parameterized slots.

2. **Anomaly Detection** — Statistical outlier detection on temperature readings. Identifies: measurement errors, illness-induced spikes, missing readings. Runs server-side on entry submission. Requires: historical temperature data per profile. Output: warning flag on insights.

3. **Symptom Insights** — Correlation analysis between symptoms and cycle phases. "You report headaches 3x more often during luteal phase." Requires: 3+ cycles of symptom data. Runs: batch, on reanalysis. Output: insight card on dashboard.

4. **Natural Language Logging** — Voice/text input: "I had light spotting and felt tired today." Parsed to structured entry (menstrual_flow=spotting, symptom=tired). Requires: NLP model or LLM. Runs: client-side or server-side. Phase: 5B+.

5. **Prediction Confidence** — Bayesian confidence scores on ovulation predictions. Replaces current binary `ovulation_confirmed`. Requires: statistical model trained on user's own data. Runs: server-side. Output: probability percentage on dashboard.

### Implementation Order

| Priority | Feature | Complexity | When |
|---|---|---|---|
| 1 | Cycle explanation (template-based) | Low | Phase 4B |
| 2 | Prediction confidence | Medium | Phase 5A |
| 3 | Symptom insights | Medium | Phase 5A |
| 4 | Anomaly detection | Low | Phase 5A |
| 5 | Natural language logging | High | ByrdOS phase |

---

## 7. Persistence Strategy — Assessment

### Current State: **Solid foundation**

- **SQLite:** Production for HA add-on. WAL mode, foreign keys ON. Single-file, zero-config. Appropriate for single-user HA deployment.
- **Alembic:** Active. Migration 001 matches current models. `create_all()` fallback removed.
- **Encryption:** AES-256-GCM per-profile. Key derived from SECRET_KEY + profile UUID via SHA-256. (ADR-0008 claims HKDF — TD-019: update ADR to match implementation).
- **Backup:** JSON export endpoint. No automated backup in HA context (rely on HA Supervisor snapshots).

### PostgreSQL Migration Path (Phase 4)

```python
# Current
DATABASE_URL = "sqlite+aiosqlite:///data/byrd_health.db"

# Future (ByrdOS)
DATABASE_URL = "postgresql+asyncpg://user:pass@host/byrd_health"
```

SQLAlchemy 2.0 async engine makes this a configuration change, not a code change. Alembic migrations must be verified against PostgreSQL before claiming support.

### Multi-User Schema Evolution

Current model is single-profile-per-instance. Multi-user requires:

1. Add `user_accounts` table (id, email, hashed_password, created_at)
2. Add `user_id` FK to `profiles` table
3. Scope all queries by `user_id`
4. Migration: existing profiles assigned to a default user

This is additive — no existing data is lost. The `get_active_profile()` function currently returns the first profile; multi-user requires `get_active_profile(user_id)`.

---

## 8. API Evolution — Assessment

### Current State: **16 REST endpoints + 1 WebSocket**

The REST API is well-structured, versioned under `/api/v1/fertility/`, and follows consistent patterns. No GraphQL needed at current scale.

### Recommendations

| Area | Current | Recommendation | Phase |
|---|---|---|---|
| **Versioning** | URL prefix (`/api/v1/`) | Keep. Proven pattern. | — |
| **OpenAPI** | Auto-generated by FastAPI | Add description, examples, error codes to schema. Document auth requirements. | Phase 4 |
| **Pagination** | Not implemented | Add `?offset=` and `?limit=` to list endpoints when cycle history grows. | Phase 4 |
| **WebSocket** | 3 message types | Add `heartbeat` for keepalive. Add `notification` for HA alert forwarding. | Phase 4 |
| **Error responses** | Inconsistent | Standardize to `{"detail": "message"}` with consistent HTTP codes. | Phase 4 |
| **Rate limiting** | None | Add in-memory rate limiter for standalone mode. Not needed for HA Ingress. | Phase 5 |
| **GraphQL** | Not implemented | **Do not add.** REST + WebSocket covers all current and planned use cases. GraphQL adds complexity without clear benefit at this scale. | Never |

---

## 9. Technical Debt Reprioritization

| Item | Old Priority | New Priority | Phase | Justification |
|---|---|---|---|---|
| TD-003 Multi-arch Docker | P1 | **Phase 4 — Prerequisite** | 4 | ARM users essential for Community Store |
| TD-010 C8 dashboard indicator | P1 | **Phase 4 — Prerequisite** | 4 | Live dashboard is Phase 3 flagship feature |
| TD-001 Pin Docker base | P1 | P1 — Phase 4 | 4 | Supply chain risk |
| TD-002 Multi-stage Docker | P1 | P1 — Phase 4 | 4 | Image size, devDeps in production |
| TD-004 Coverage reporting | P1 | P1 — Phase 4 | 4 | Visibility into untested code |
| TD-005 pip-audit scanning | P1 | P1 — Phase 4 | 4 | Health data platform needs vuln scanning |
| TD-006 Graphify key_fields | P1 | P1 — Phase 4 | 4 | Graphify accuracy |
| TD-007 IngressMiddleware consolidation | P1 | P2 — Phase 5 | 5 | Intentional duplication per ADR-0006; low risk |
| TD-008 Schema consolidation | P1 | P1 — Phase 4 | 4 | Blocks module expansion |
| TD-009 Pre-commit/CI alignment | P1 | P2 — Phase 4 | 4 | Non-blocking quality of life |
| TD-012 Archive obsolete docs | P2 | ✅ Done (3.5-A) | — | Completed |
| TD-013 Remove duplicate tests | P2 | ✅ Done (3.5-B) | — | Completed |
| TD-016/017 ADR/phase updates | P2 | ✅ Done (3.5-A) | — | Completed |
| TD-020 Create Graphify nodes | P2 | ✅ Done (3.5-D) | — | Completed |
| TD-021/022/023 Dead code | P2 | ✅ Done (3.5-C) | — | Completed |
| TD-032/033/034 Cleanup | P2 | ✅ Done (3.5) | — | Completed |
| TD-018 ADR-0011 endpoint fix | P2 | P2 — Phase 4 | 4 | ADR accuracy |
| TD-019 ADR-0008 encryption fix | P2 | P2 — Phase 4 | 4 | Security documentation accuracy |
| TD-014 Async test standardization | P2 | P2 — Phase 4 | 4 | Test quality |
| TD-015 Timing-dependent tests | P2 | P2 — Phase 5 | 5 | Non-trivial refactor |
| TD-027/028 Model naming | P3 | P3 — Never | — | Breaking change without benefit |
| TD-030/031/024/025/026 | P3 | P3 — Phase 4-5 | 4-5 | Minor improvements |

---

## 10. Roadmap

| Milestone | Content | Est. Duration |
|---|---|---|
| **Phase 4A** | Prerequisites: C8 fix, multi-arch Docker. Pregnancy tracking (extension of fertility). Branding assets. OpenAPI docs. | 2-4 weeks |
| **Phase 4B** | Symptoms catalog. Medication tracking. Cycle explanation (AI template). Notification improvements. | 4-6 weeks |
| **Phase 4C** | Sleep tracking. Sleep-scoring engine. Time-series visualization. | 4-6 weeks |
| **Phase 4D** | Nutrition tracking. Food database. Meal planning. | 4-6 weeks |
| **Phase 5A** | Wearable integration (Apple Health, Google Fit, Garmin, Fitbit). Prediction confidence (AI). Symptom insights. Anomaly detection. | 6-8 weeks |
| **Phase 5B** | Standalone auth (OAuth2/JWT). Multi-user data model. PostgreSQL production support. Natural language logging. | 6-8 weeks |
| **ByrdOS Migration** | ByrdOSBridge replaces HABridge. Message queue (Redis). Service discovery. Multi-instance WebSocket. | TBD |

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Schema duplication causes drift across new modules | High | High | Consolidate schemas in Phase 4 before adding modules (TD-008) |
| C8 indicator defect is a React rendering issue, not a WebSocket issue | Medium | High | Investigate in Phase 4A prerequisite |
| ARM builds add 4-8x CI time | High | Medium | Use QEMU emulation initially; accept slower builds |
| Multi-user migration breaks existing single-user data | Low | High | Additive migration; test on copy of production DB |
| New modules bloat the frontend bundle | Medium | Medium | Route-based code splitting already implemented; per-module entry points |
| Community Store submission delayed by missing branding | Medium | Low | Generate assets in Phase 4A |

---

## Phase 4 Recommendation: **GO ✅ — Conditional**

**Prerequisites before Phase 4 feature work begins:**

1. ✅ Phase 3.5 maintenance complete
2. ⬜ 3A.8 — Frontend WebSocket contract alignment
3. ⬜ TD-003 — Multi-arch Docker builds (amd64 + arm64)
4. ⬜ TD-010 — C8 dashboard indicator investigation

**Phase 4 may begin immediately on non-blocking items** (branding, OpenAPI, pregnancy tracking research) while the 3 prerequisites are completed.

**Overall architecture assessment:** The foundation is solid. The modular monolith pattern scales well for the next 2-3 modules. Re-evaluate after Phase 4C whether to extract a shared `core` package.
