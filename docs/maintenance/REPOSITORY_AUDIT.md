# Repository Audit

## Dead Files

| File | Lines | Issue |
|------|-------|-------|
| `frontend/src/lib/mock-data.ts` | 287 | Zero consumers |
| `temp_body.json` | — | Root leftover artifact |

## Dead Functions

| Function | Location | Issue |
|----------|----------|-------|
| `estimate_baseline()` | `coverline.py` | Zero production callers |
| `DashboardResponse` | `responses.py` | Pydantic model — no route returns it |

## Unused Export Aliases

7 router aliases in `routers/__init__.py` that nobody imports.

## Duplicate Code

- **IngressMiddleware** duplicated in `ha_bridge/ingress.py` and `web_api/ingress.py`
- **Schema classes** duplicated between `data_service/schemas.py` and `web_api/schemas/responses.py` (6 overlapping classes)
- **`_to_date()`** helper duplicated in `analysis.py` and `fertile_window.py`
- **`config.yaml`** duplicated at root and `repository/`
- **`repository.yaml`** also duplicated

## Obsolete Files

| Path | Reason |
|------|--------|
| `legacy/` directory (21 entries) | v1.0.4 Flask app, never imported |
| `legacy/tests/` | Tests obsolete Flask routes |
| `PROJECT_IDEA.md` | Empty file (0 bytes) |

## Stale Scripts

| Script | Issue |
|--------|-------|
| `tools/find-ingress.mjs` | Ad-hoc diagnostic, not integrated into any workflow |

## Naming Inconsistencies

- **TypeScript types** in `fertility.ts` mix snake_case (API-matching) with camelCase (`cycleId`, `lastTemp`)
- **SQLAlchemy models:** `FertilitySigns` (plural) and `ComputedInsights` (plural) should be singular to match `Profile`, `Cycle`, `Temperature`, `Symptom`

## Broken References

9 files reference `docs/LEGACY_REVIEW.md` which moved to `docs/archive/` (8 ADRs + `PROMPT.md`)

## Structure Issues

- `test-results/` not in `.gitignore`
- Root `package.json` needed for Playwright but poorly documented
- `byrd_health_test.db` artifacts at root
- `packages/web_api/pyproject.toml` missing `ha-bridge` in dependencies
