# Phase 4B Readiness Assessment

> **Date:** 2026-07-26 | **Reviewer:** Architect  
> **M1 Gate:** APPROVED WITH CONDITIONS  
> **Phase 4B Verdict:** GO — after conditions satisfied

---

## Prerequisites Status

| # | Condition | Status | Owner |
|---|---|---|---|
| C1 | Remove false Graphify edge `pregnancy-engine → data-service` | Pending | Graphify Engineer |
| C2 | Refactor PregnancyPage to use `@tanstack/react-query` | Pending | Frontend Engineer |

**Both must be resolved before Phase 4B dispatch.**

---

## Phase 4B Scope Review

### Symptoms & Medications Catalog — Architecture Fit

#### Data Layer
- **`SymptomCatalog` table** — New table in `data_service/models.py`. References existing `symptoms` table by `symptom_type` string. Additive — no migration of existing data required.
- **`Medication` table** — New standalone table. FK to `profiles`. Additive.
- **Pattern:** Both tables follow the established SQLAlchemy model conventions. No schema redesign needed.

#### API Layer
- **`GET /api/v1/fertility/symptoms/catalog`** — New endpoint in a new router. Returns catalog entries.
- **`GET/POST /api/v1/fertility/medications`** — New endpoints. Standard CRUD.
- **Pattern:** Follows existing router conventions. Requires `summary`, `description`, and `responses` dicts (lesson from C4).

#### Frontend Layer
- **Symptom catalog picker** — Replaces free-text symptom input with structured catalog selection. Existing `EntryForm.tsx` must be modified to support catalog-based lookup.
- **Medication log** — New page. Must use `@tanstack/react-query` hooks (lesson from C2).
- **Pattern:** New pages follow the established React Query pattern. Existing forms modified incrementally.

---

### Work Packages (from WBS)

| ID | Task | Owner | Est. | Complexity | Dependencies |
|---|---|---|---|---|---|
| 4B.1 | Symptom catalog data model | DB | 2h | S | M1 cleared |
| 4B.2 | Medication tracking model | DB | 2h | S | M1 cleared |
| 4B.3 | Symptom catalog REST | BE | 1h | S | 4B.1 |
| 4B.4 | Medication REST | BE | 2h | S | 4B.2 |
| 4B.5 | Symptom catalog frontend | FE | 3h | M | 4B.3 |
| 4B.6 | Medication frontend | FE | 3h | M | 4B.4 |
| 4B.7 | HA entities update | HAE | 2h | S | 4B.3, 4B.4 |
| 4B.8 | WebSocket heartbeat | BE | 1h | S | — |
| 4B.9 | Integration test + Graphify | QA+GRAPH | 1h | S | All 4B |

**Total: 9 work packages, 17 estimated hours.**

---

### Critical Path

```
4B.1 ──> 4B.3 ──> 4B.5 ──> 4B.7
4B.2 ──> 4B.4 ──> 4B.6 ──┘
4B.8 (parallel)
4B.9 (after all)
```

Critical path length: 4 sequential tasks. No long blocking chains. Should complete in 2-3 dispatch rounds.

---

### Architecture Boundaries Check

| Boundary | Phase 4B Impact | Verdict |
|---|---|---|
| `fertility_engine` isolation | No changes. Symptoms/medications don't require new algorithms. | ✅ No impact |
| `data_service` isolation | Two new tables. No new imports from other packages. | ✅ No impact |
| `web_api` dependencies | New router. May import `data_service` schemas. | ✅ Allowed |
| `ha_bridge` isolation | New entities published. No new imports into bridge. | ✅ No impact |
| `device_adapters` isolation | No changes. | ✅ No impact |
| `frontend` HTTP-only | New API calls. No Python imports. | ✅ Allowed |
| Circular dependencies | Zero introduced by 4B. | ✅ Verified |

---

### Risk Assessment

| Risk | Mitigation |
|---|---|
| Symptom catalog migration conflicts with existing free-text `symptoms` table | Additive — catalog is a separate table. Existing symptoms unaffected. |
| Medication model needs scheduling/reminder logic beyond Phase 4B scope | Limit to CRUD in Phase 4B. Scheduling deferred to Phase 5. |
| Frontend symptom picker requires EntryForm redesign | Incremental change — add catalog lookup alongside existing free-text. Both can coexist. |
| Backend Engineer bottleneck (4B.3, 4B.4, 4B.8 = 4h sequential) | Acceptable — total BE time is 4h across 3 tasks. DB can work in parallel. |
| C2 (React Query) not fixed before 4B frontend pages built | **Blocking condition.** C2 must be fixed first. |

---

### Lessons Applied from Phase 4A

| Lesson | Applied To |
|---|---|
| All routers must include `responses` dicts | 4B.3, 4B.4 — Backend Engineer requirement |
| All frontend pages must use React Query hooks | 4B.5, 4B.6 — Frontend Engineer requirement |
| Graphify edges must be verified before commit | 4B.9 — QA verification step |
| Engine packages only created when computation is needed | Phase 4B has NO new engine (symptoms/meds are data modules) |
| Migration must be additive | 4B.1, 4B.2 — Database Engineer requirement |
| OpenAPI `description` on all endpoints | 4B.3, 4B.4 — Backend Engineer requirement |

---

### Success Metrics for Phase 4B

| Metric | Current | Phase 4B Target |
|---|---|---|
| Python tests | 285 | 300+ |
| Packages | 6 | 6 (no new engine needed) |
| HA entities | 9 | 12+ |
| REST endpoints | 19 | 22+ |
| Frontend pages | 8 | 10 |
| WebSocket types | 2 | 3 (+heartbeat) |
| Graphify accuracy | 99% | 100% |

---

## Verdict: GO — after C1 and C2 resolved

Phase 4B is well-scoped, fits the architecture cleanly, and benefits from lessons learned in Phase 4A. The symptom catalog and medication modules are data-catalog extensions rather than computation modules, which keeps complexity low and package count stable.

**Two conditions before dispatch:**

1. **C1:** Remove false Graphify edge (5 min, Graphify Engineer)
2. **C2:** Refactor PregnancyPage to React Query (1 hr, Frontend Engineer)

Once these are resolved, Phase 4B may begin immediately. No further architectural review is required for this scope.
