# Phase 4 Milestone Gates

> **Date:** 2026-07-26 | **Gates:** 6 | **Validation:** Per-gate evidence required

---

## Gate Progression

```
Current (Phase 3 Complete)
        │
        ▼
M0 — Prerequisites Cleared ─────── (3 items)
        │
        ▼
M1 — Phase 4A Complete ────────── (Pregnancy tracking)
        │
        ▼
M2 — Phase 4B Complete ────────── (Symptoms & Medications)
        │
        ▼
M3 — Phase 4C Complete ────────── (Sleep tracking)
        │
        ▼
M4 — Phase 4D Complete ────────── (Nutrition tracking)
        │
        ▼
M5 — RC2 Ready ────────────────── (Release Candidate 2)
        │
        ▼
M6 — Community Release Candidate
```

---

## M0 — Prerequisites Cleared

**Blocks:** All Phase 4 feature work

| Criterion | Evidence | Owner |
|---|---|---|
| PREQ-1 complete | `useWebSocket.ts` types match `WEBSOCKET_PROTOCOL.md` §6.2. `npm run build` passes. | Frontend Engineer |
| PREQ-2 complete | `container-build.yml` pushes `linux/amd64` + `linux/arm64`. Image pulls on ARM emulation. | DevOps Engineer |
| PREQ-3 complete | Dashboard shows "Live" with green dot within 10s on live HA via Ingress. VS-2 C5+C8 pass. | Frontend Engineer |
| Full test suite | 255+ tests pass. | QA Engineer |

**Exit gate:** All 3 prerequisites resolved. Architect verifies and signs off.

---

## M1 — Phase 4A Complete (Platform Hardening + Pregnancy)

**Depends on:** M0 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| Schema consolidation done | No duplicated Pydantic models across `data_service` and `web_api`. `git grep "class ProfileResponse"` returns 1 result. | Backend Engineer |
| ADRs updated | ADR-0011 §2.4 corrected. ADR-0008 encryption claim corrected. | Architect |
| Error responses standardized | All `HTTPException` calls use consistent format. | Backend Engineer |
| Pregnancy data model exists | `Pregnancy` table in DB. Migration `_002` applies cleanly. | Database Engineer |
| Pregnancy engine works | `calculate_due_date()` returns correct date. Tests pass. | Backend Engineer |
| Pregnancy REST works | `GET/POST /api/v1/fertility/pregnancy` returns correct data. | Backend Engineer |
| Pregnancy frontend renders | Pregnancy dashboard page visible via Ingress. Due date, week, trimester displayed. | Frontend Engineer |
| Cycle explanation renders | Template-based explanation appears in insights response. | Backend Engineer |
| Branding assets ready | `icon.png`, `logo.png` in repository. `config.yaml` has all metadata fields. | Documentation Engineer |
| OpenAPI documented | `/docs` shows all endpoints with descriptions and error codes. | Backend Engineer |
| Graphify updated | `pregnancy_engine` service node created. `Pregnancy` entity node created. Phase 4A milestone marked complete. | Graphify Engineer |
| Full test suite | 255+ tests pass. New pregnancy tests included. | QA Engineer |

**Exit gate:** All 12 criteria met. Architect verifies. Release Engineer runs VS-3 (pregnancy workflow validation on live HA).

---

## M2 — Phase 4B Complete (Symptoms & Medications)

**Depends on:** M1 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| Symptom catalog seeded | `SymptomCatalog` table populated with common symptoms. | Database Engineer |
| Medication model exists | `Medication` table in DB. Migration applies cleanly. | Database Engineer |
| Symptom catalog API works | `GET /api/v1/fertility/symptoms/catalog` returns catalog. | Backend Engineer |
| Medication API works | `GET/POST /api/v1/fertility/medications` works. | Backend Engineer |
| Structured symptom picker | Frontend replaces free-text with catalog picker. | Frontend Engineer |
| Medication log UI | Medication tracking dashboard renders. | Frontend Engineer |
| HA entities updated | Pregnancy + symptom + medication entities published to HA. | HA Engineer |
| WebSocket heartbeat active | `heartbeat` message type emitted, client responds. | Backend Engineer |
| Graphify updated | New entities and milestone added. | Graphify Engineer |
| Full test suite | All tests pass. New 4B tests included. | QA Engineer |

**Exit gate:** All 10 criteria met. Architect verifies.

---

## M3 — Phase 4C Complete (Sleep Tracking)

**Depends on:** M2 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| Sleep engine works | Sleep scoring, debt calculation. Tests pass. | Backend Engineer |
| Sleep data model exists | `SleepSession` table. Migration applies. | Database Engineer |
| Sleep API works | `GET/POST /api/v1/fertility/sleep` works. | Backend Engineer |
| Sleep frontend renders | Sleep chart, weekly trends visible. | Frontend Engineer |
| Cross-module correlation | Sleep quality by cycle phase insight works. | Backend Engineer |
| Graphify updated | `sleep_engine` node, `SleepSession` entity. | Graphify Engineer |
| Full test suite | All tests pass. | QA Engineer |

**Exit gate:** All 7 criteria met. Architect verifies.

---

## M4 — Phase 4D Complete (Nutrition Tracking)

**Depends on:** M3 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| Nutrition engine works | Macro calculation. Tests pass. | Backend Engineer |
| Nutrition data model exists | `FoodItem`, `Meal`, `MealItem` tables. | Database Engineer |
| Nutrition API works | `GET/POST /api/v1/fertility/nutrition` works. | Backend Engineer |
| Nutrition frontend renders | Meal logger, macro dashboard visible. | Frontend Engineer |
| Graphify updated | `nutrition_engine` node, entities. | Graphify Engineer |
| Full test suite | All tests pass (est. 350+). | QA Engineer |

**Exit gate:** All 6 criteria met. Architect verifies.

---

## M5 — RC2 Ready (Release Candidate 2)

**Depends on:** M4 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| All Phase 4 features functional | Pregnancy, symptoms, medications, sleep, nutrition all work end-to-end on live HA. | Release Engineer |
| Multi-arch Docker images | `linux/amd64` + `linux/arm64` images on GHCR. | DevOps Engineer |
| VS-3 validation suite | Playwright suite covering all new features. | QA Engineer |
| VS-3 executed | All checks pass on live HA instance. | Release Engineer |
| CHANGELOG updated | v2.2.0 release notes with all Phase 4 features. | Architect |
| Documentation updated | README, ARCHITECTURE, USER_GUIDE reflect Phase 4. | Documentation Engineer |
| Graphify current | 100% index accuracy. | Graphify Engineer |
| Known issues documented | `docs/releases/KNOWN_ISSUES.md` updated. | Release Engineer |
| 350+ tests pass | Full test suite. Coverage ≥ 80%. | QA Engineer |

**Exit gate:** All 9 criteria met. Release Engineer certifies RC2.

---

## M6 — Community Release Candidate

**Depends on:** M5 cleared

| Criterion | Evidence | Owner |
|---|---|---|
| HA Community Store compliance | Add-on meets all Community Store guidelines. | HA Engineer |
| Branding complete | Icon, logo, screenshots, description. | Documentation Engineer |
| Multi-arch verified | Images tested on amd64 + arm64 hardware/emulation. | DevOps Engineer |
| Release notes published | GitHub Release with changelog. | Release Engineer |
| Beta testing period | 2+ weeks of user testing without critical bugs. | All |

**Exit gate:** Community Store submission package ready. Architect approves final release.
