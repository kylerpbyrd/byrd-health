# M1 Certification — Phase 4A Gate Review

> **Date:** 2026-07-26 | **Reviewer:** Architect (final review)  
> **Gate:** M1 — Phase 4A Complete  
> **Verdict:** APPROVED WITH CONDITIONS

---

## Milestone Audit

### Deliverable Verification (11 work packages)

| # | Deliverable | Planned | Delivered | Status |
|---|---|---|---|---|
| 4A.1 | Schema consolidation (TD-008) | 6 duplicated classes → 1 canonical source | 6 classes re-exported from data_service | ✅ PASS |
| 4A.2 | Branding assets | Icon, logo, config metadata | Config updated, icon.svg placeholder | ✅ PASS |
| 4A.3 | OpenAPI documentation | All endpoints documented | 20 REST endpoints documented; pregnancy router missing `responses` dicts | ⚠️ PARTIAL |
| 4A.4 | Pregnancy data model | SQLAlchemy model + migration | Model, migration `_002`, repository | ✅ PASS |
| 4A.5 | Pregnancy engine | Calculator package, 7 tests | Calculator package, 7 tests, 4 public functions | ✅ PASS |
| 4A.6 | Pregnancy REST endpoints | 3 endpoints with tests | 3 endpoints, router registered, tests exist | ✅ PASS |
| 4A.7 | Pregnancy frontend | Dashboard page with start tracking | Page, route, nav link. Uses raw fetch instead of React Query | ⚠️ PASS (pattern concern) |
| 4A.8 | Error standardization | Consistent `{"detail": "..."}` | Pregnancy router consistent. Retrofit applied to 6 existing responses. | ✅ PASS |
| 4A.9 | Cycle explanation | Template-based, deterministic | `generate_explanation()` — deterministic, no AI/LLM deps | ✅ PASS |
| 4A.10 | ADR accuracy | ADR-0011 endpoint, ADR-0008 encryption | Both ADRs corrected with implementation notes | ✅ PASS |
| 4A.11 | Graphify sync | 3 new nodes, edges, index | Nodes created. One edge factually wrong (C1). | ⚠️ PASS (1 fix needed) |

**9 of 11 fully verified. 2 with minor issues requiring remediation.**

---

### M1 Exit Criteria (12)

| # | Criterion | Status |
|---|---|---|
| 1 | Schema consolidation done | ✅ |
| 2 | ADRs updated | ✅ |
| 3 | Error responses standardized | ✅ |
| 4 | Pregnancy data model exists | ✅ |
| 5 | Pregnancy engine works | ✅ |
| 6 | Pregnancy REST works | ✅ |
| 7 | Pregnancy frontend renders | ✅ (pattern divergence noted) |
| 8 | Cycle explanation renders | ✅ |
| 9 | Branding assets ready | ✅ |
| 10 | OpenAPI documented | ⚠️ (pregnancy router missing responses dicts) |
| 11 | Graphify updated | ⚠️ (false edge: pregnancy-engine → data-service) |
| 12 | Full test suite passes | ✅ (285 tests, 0 failures) |

**10 of 12 criteria verifiably PASS. 2 need fixes (C1, C4).**

---

## Regression Review

### Package Boundaries: No violations introduced
- `pregnancy_engine` has zero imports from any sibling package — follows the `fertility_engine` isolation pattern
- `web_api → pregnancy_engine` dependency is declared correctly
- No circular dependencies introduced
- **Minor concern (C7):** Pregnancy router imports `sqlalchemy.inspect` (SQLAlchemy internal API) — routers should not depend on ORM internals

### Dependency Direction: One false edge in Graphify
- **C1 (High):** Graphify edge `pregnancy-engine → data-service` (DEPENDS_ON) is factually incorrect. PregnancyEngine has zero imports from DataService. This edge must be removed.
- **C3 (Medium):** `DEPENDENCY_GRAPH.md` not updated — missing pregnancy_engine row, external deps, and current test count (shows 255, should be 285).

### REST Consistency: Two issues
- **C4 (Medium):** Pregnancy router endpoints lack `responses={404: ..., 409: ...}` dicts — inconsistent with other routers that have them
- **C8 (Low):** Trailing slash mismatch between frontend (`/pregnancy`) and backend (`/pregnancy/`) — POST requests may lose body on 307 redirect

### Frontend Consistency: Pattern divergence
- **C2 (Medium):** `PregnancyPage` uses raw `useState`/`useEffect`/`fetch` instead of `@tanstack/react-query` hooks. All other pages (Dashboard, History, Profiles, Settings) use React Query for data fetching, caching, and invalidation. This is a significant architectural pattern divergence.

### Database Evolution: Clean
- Migration `_002_add_pregnancy` is additive (creates table only). Downgrade drops table cleanly. No data migration required. No existing data affected.

### Migration Safety: Verified
- `upgrade()` creates `pregnancies` table. `downgrade()` drops it. Both verified functional.

### OpenAPI Accuracy: Partial
- 20 endpoints have `summary`/`description`. Pregnancy router has `summary` only — missing `description` and `responses` dicts.

### Graphify Accuracy: One correction needed
- **C1:** Remove false `pregnancy-engine → data-service` edge. Add correct edge if applicable (none needed — pregnancy_engine is isolated like fertility_engine).

---

## Pregnancy Module Assessment

### Module Architecture: Follows the established pattern

```
pregnancy_engine/          ← Pure Python, zero framework deps (matches fertility_engine)
data_service/models.py     ← Pregnancy SQLAlchemy model (extends existing data layer)
data_service/migrations/   ← Alembic migration (additive, no data migration)
web_api/routers/           ← Pregnancy router (matches existing router patterns)
frontend/src/pages/        ← PregnancyPage (follows page component structure)
```

### Separation from Fertility Engine: Clean
- `pregnancy_engine` is a completely separate package. Zero imports from `fertility_engine`. The two modules interact only through the `web_api` orchestration layer — pregnancy reads cycle data via `data_service`, not by importing fertility logic.

### Future Extensibility: Good foundation
- The `Pregnancy` model can be extended with trimester-specific fields, appointment tracking, weight tracking, symptoms, kick counts, etc. — all additive, no schema redesign needed.
- The `pregnancy_engine` can grow to include trimester milestone data, weight gain recommendations, appointment scheduling — pure functions, zero framework deps.

### Database Design: Follows established patterns
- UUID PK, FK with CASCADE, timestamps with server defaults, relationship back-populates
- `cycle_id` is unique (one-to-one with cycle) — correct for the domain model
- `profile_id` enables multi-profile support
- `is_active` flag supports ending tracking without deleting data

### API Surface: Clean, RESTful
- 3 endpoints covering the full lifecycle: start, read, update/end
- Follows existing authentication model (HA Ingress, `get_active_profile`)
- Response includes computed fields (current_week, days_remaining) updated on each GET

### Frontend Architecture: Concern noted
- **Recommendation:** Refactor `PregnancyPage` to use `@tanstack/react-query` before Phase 4B begins. Create a `usePregnancy` hook following the `useDashboard`/`useCycles`/`useProfile` pattern. This ensures cache consistency with other pages and avoids the stale-data problems that raw `useEffect` introduces.

### Testing Strategy: Adequate for Phase 4A
- 7 unit tests for pregnancy_engine (date math edge cases)
- 8 integration tests for pregnancy REST endpoints
- Missing: frontend tests for PregnancyPage
- Missing: edge case tests (concurrent pregnancy creation, ending an already-ended pregnancy)

### Recommendations Before Additional Modules

1. **Standardize the frontend data-fetching pattern** — All new pages must use `@tanstack/react-query` hooks. The PregnancyPage raw-fetch pattern should not be replicated.
2. **Standardize the router template** — All new routers must include `summary`, `description`, and `responses` dicts.
3. **Fix the Graphify edge** — Remove the false `pregnancy-engine → data-service` edge.
4. **Update DEPENDENCY_GRAPH.md** — Add pregnancy_engine row, external deps, and current test count.

---

## AI Review: Cycle Explanation System

### Determinism: ✅ Fully deterministic
- `generate_explanation()` has zero non-deterministic inputs: no `random`, no `datetime.now()`, no external API calls, no file reads. Same inputs always produce same output.

### Explainability: ✅ Produces human-readable output
- Templates are parameterized with named slots: `{coverline}`, `{ovulation_day}`, `{method}`, `{phase}`, `{luteal_length}`. Output is natural English prose, not raw data.

### No Hidden AI Dependencies: ✅ Confirmed
- Zero imports of ML, LLM, or AI libraries. Pure Python string formatting. No `openai`, `transformers`, `sklearn`, `tensorflow`, `pytorch`.

### ADR-0007 Alignment: ✅ Matches Layer 1 (Rules Engine)
- ADR-0007 specifies a 2-layer architecture: Layer 1 (deterministic rules) + Layer 2 (ML models, Phase 4+). The explanation system is Layer 1 — it consumes the deterministic `CycleInsights` output and transforms it into prose without ML.

### Future LLM Integration Path
The current template-based system is a solid foundation for future LLM enhancement:

1. **Fallback pattern:** If LLM is unavailable (offline, ByrdOS privacy constraint), fall back to templates — exactly the current implementation.
2. **Prompt engineering:** The template slots map directly to LLM prompt variables: `{coverline}`, `{ovulation_day}`, `{method}`, etc.
3. **No retraining needed:** The template output serves as training examples for fine-tuning if desired.
4. **Confidence scoring:** Could add a `confidence` field to the response (1.0 for templates, <1.0 for LLM-generated) — this is an ADR-0007 `PredictionModel` integration point.

---

## Technical Debt Update

### New Debt Introduced (9 items)

| ID | Item | Severity | Recommendation |
|---|---|---|---|
| C1 | False Graphify edge: pregnancy-engine → data-service | High | Remove edge. Fix in Phase 4A remediation. |
| C2 | PregnancyPage uses raw fetch instead of React Query | Medium | Refactor to useQuery/useMutation hooks. Fix before Phase 4B. |
| C3 | DEPENDENCY_GRAPH.md out of date | Medium | Add pregnancy_engine. Update test count to 285. |
| C4 | Pregnancy router missing OpenAPI responses dicts | Medium | Add responses to all 3 endpoints. |
| C5 | PregnancyResponse type missing profile_id | Low | Add to TypeScript interface. |
| C6 | pregnancy_engine declares unused pydantic dep | Low | Remove or add Pydantic models. |
| C7 | Router imports sqlalchemy.inspect (layering) | Low | Move to repository or response builder. |
| C8 | Trailing slash redirect risk on POST | Low | Add redirect_slashes=False or match URLs. |
| C9 | API error extraction pattern inconsistent | Low | Extract server error detail from response body. |

### Debt Resolved in Phase 4A

| ID | Item |
|---|---|
| TD-008 | Schema consolidation — DONE |
| TD-018 | ADR-0011 endpoint fix — DONE |
| TD-019 | ADR-0008 encryption claim fix — DONE |
| TD-003 | Multi-arch Docker builds — DONE |
| TD-010 | C8 dashboard indicator — DONE |

### Debt Promotion Recommendation

**Promote to Phase 4B prerequisite:** C1 (false Graphify edge), C2 (React Query pattern). These two items should be fixed before any new modules are built — C2 because it establishes the pattern for all future frontend pages, and C1 because stale Graphify is a project defect.

**Defer to Phase 4B backlog:** C3, C4, C5, C6, C7, C8, C9 — all non-blocking polish items.

---

## Release Readiness

### RC2 Status

| Metric | Current | RC2 Target | Status |
|---|---|---|---|
| Python tests | 285 | 350+ | On track |
| Packages | 6 (+1) | 7+ | On track |
| HA entities | 9 per profile | 12+ | Phase 4B |
| Frontend pages | 8 (+1) | 10+ | On track |
| Docker architectures | 2 (amd64+arm64) | 2 | DONE |
| Graphify accuracy | 86 nodes, 1 false edge | 100% accurate | 1 fix needed |
| Known issues | 1 (C8 — resolved) | ≤ 3 | C1-C2 are new known issues |

### Phase 4B Risk Assessment

**Risk: Replicating the React Query pattern divergence.** If Phase 4B frontend pages (symptom catalog, medication log) also use raw `useEffect` + `fetch`, the codebase will have two competing data-fetching patterns. This increases maintenance burden and makes cache invalidation inconsistent across pages.

**Mitigation:** Fix C2 (refactor PregnancyPage to React Query) before Phase 4B begins. Use the `usePregnancy` hook as the template for `useSymptomCatalog` and `useMedications`.

---

## Phase 4B Planning Review

### Symptoms & Medications Scope: Architecture Fit

✅ **Fits current architecture.** The proposed module follows the established pattern:
- New data tables (`SymptomCatalog`, `Medication`) in `data_service` — additive, no schema redesign
- New REST endpoints in `web_api/routers/` — no new packages needed yet
- New frontend pages — route-based lazy loading supports expansion
- Existing package boundaries remain valid — no new cross-package dependencies needed

✅ **No schema redesign required.** The `SymptomCatalog` table adds a structured symptom reference without modifying the existing free-text `symptoms` table. The `Medication` table is standalone.

✅ **Existing APIs support expansion.** The REST API follows a consistent prefix pattern (`/api/v1/fertility/{module}`) that accommodates new modules without affecting existing endpoints.

✅ **Package boundaries remain valid.** No new engine package is required for Phase 4B — symptoms and medications are data-catalog modules, not computation modules. Sleep (Phase 4C) will require a new `sleep_engine` package.

### Recommendations Before Phase 4B Implementation

1. **Fix C1 and C2** (false Graphify edge + React Query pattern) as Phase 4B prerequisites
2. **Create a `usePregnancy` hook** as the reference implementation for future frontend data-fetching hooks
3. **Document the router template** — every new router must include `summary`, `description`, and `responses` dicts
4. **Update DEPENDENCY_GRAPH.md** — add pregnancy_engine row before adding more packages

---

## Verdict: APPROVED WITH CONDITIONS

Phase 4A is substantially complete and meets the architectural standards. Two conditions must be satisfied before Phase 4B begins:

| Condition | Severity | Owner | Est. |
|---|---|---|---|
| **C1:** Remove false Graphify edge `pregnancy-engine → data-service` | High | Graphify Engineer | 5 min |
| **C2:** Refactor PregnancyPage to use `@tanstack/react-query` hooks | Medium | Frontend Engineer | 1 hr |

Once these two conditions are met, Phase 4B may proceed without restriction. The remaining 7 concerns (C3-C9) are non-blocking polish items for the Phase 4B backlog.
