# Phase 3.5 — Repository Maintenance and Hardening Plan

> **Date:** 2026-07-26 | **Sources:** REPOSITORY_AUDIT.md, TECH_DEBT.md, TEST_AUDIT.md

---

## Scope

Structured cleanup of all non-feature technical debt identified in the M4 audit. Five workstreams, ordered by dependency. Each workstream produces a commit. Test suites must pass after each workstream.

---

## Workstream A — Documentation Cleanup

**Debt items:** TD-011, TD-012, TD-016, TD-017, TD-034

| # | Action | Risk |
|---|---|---|
| A1 | Fix 9 broken `LEGACY_REVIEW.md` references in ADRs + PROMPT.md | None — path fix |
| A2 | Archive 10 obsolete docs to `docs/archive/` | None — move only |
| A3 | Update README: phase "Phase 3 Complete", ADRs 13, packages 5 | None |
| A4 | Update ARCHITECTURE.md: add ADR-0013 row, fix HA Bridge label | None |
| A5 | Add archival notice LEGACY.md in `legacy/` | None |
| A6 | Populate or delete `PROJECT_IDEA.md` | None — empty file |

---

## Workstream B — Test Cleanup

**Debt items:** TD-013, TD-032, plus low-value test fixes

| # | Action | Risk |
|---|---|---|
| B1 | Remove `fertility_engine/tests/test_regression.py` | None — 100% duplicate |
| B2 | Remove `legacy/tests/test_routes.py` and `test_algorithms.py` | None — obsolete |
| B3 | Remove `device_adapters/tests/test_protocol.py` | None — tests isinstance |
| B4 | Fix `test_register_adds_adapter` (replace `assert True`) | Low — add real assertion |
| B5 | Fix `test_full_pipeline_conservative_method` (add meaningful assertions) | Low |
| B6 | Fix `test_request_returns_json_on_success` (add assertions) | Low |
| B7 | Fix `test_bridge_start_polling_adds_sensor` (add assertions) | Low |
| B8 | Remove `frontend/src/__tests__/Skeleton.test.tsx` | None — CSS-only |
| B9 | Write TESTING_CONVENTIONS.md | None |

---

## Workstream C — Dead Code and Duplicate Code

**Debt items:** TD-007, TD-021, TD-022, TD-023, TD-033

| # | Action | Risk |
|---|---|---|
| C1 | Delete `frontend/src/lib/mock-data.ts` | None — zero consumers |
| C2 | Delete `temp_body.json` | None — artifact |
| C3 | Remove `estimate_baseline()` from coverline.py + its tests | **Low** — exported, zero production callers |
| C4 | Remove `DashboardResponse` from responses.py + schemas/__init__.py | None — no route returns it |
| C5 | Clean `routers/__init__.py` — remove unused aliases | None — no consumers |
| C6 | Consolidate IngressMiddleware — keep `web_api/ingress.py`, make `ha_bridge` import from web_api, or remove ha_bridge copy | **Medium** — cross-package dependency |
| C7 | Update `.gitignore`: add `test-results/`, `*.db-shm`, `*.db-wal` | None |

---

## Workstream D — Graphify Synchronization

**Debt items:** TD-006, TD-020, TD-026

| # | Action | Risk |
|---|---|---|
| D1 | Fix 5 entity node key_fields to match SQLAlchemy models | None |
| D2 | Create 18 missing node files (7 entities, 1 function, 1 milestone, 9 docs) | None |
| D3 | Fix 4 reversed timestamps | None |

---

## Workstream E — Dependency and CI Consistency

**Debt items:** TD-009, TD-029

| # | Action | Risk |
|---|---|---|
| E1 | Add `ha-bridge` to `web_api/pyproject.toml` dependencies | None |
| E2 | Align pre-commit mypy with CI: remove `--strict` from pre-commit (CI has relaxed config) | **Low** — change tooling |
| E3 | Verify `eslint` reference in CI — remove if not configured | None |
| E4 | Run full test suite after all changes | None |

---

## Deferred to Phase 4

| Item | Reason |
|---|---|
| TD-001 through TD-005 | Docker/CI security — Phase 4 P1 items |
| TD-008 | Schema consolidation — architectural review needed |
| TD-010 | C8 dashboard indicator — investigation needed |
| TD-014 | Async test standardization — deeper refactor |
| TD-015 | Timing-dependent tests — deeper refactor |
| TD-018, TD-019 | ADR fixes — spec change, needs approval |
| TD-024 through TD-028, TD-030, TD-031 | Low-priority consistency items |

---

## Execution Order

```
A (Docs) → B (Tests) → C (Dead Code) → D (Graphify) → E (CI/Deps)
                                                          │
                                                     Full test suite
                                                          │
                                                     Exit gate
```

Tests must pass after each workstream commit.
