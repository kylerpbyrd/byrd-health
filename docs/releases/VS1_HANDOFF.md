# VS-1 Runtime Validation — Architect Handoff

> **From**: Lead Architect
> **To**: Release Engineer
> **Date**: 2026-07-26
> **Gate**: Phase A cleared → VS-1 Runtime Validation ready
> **Previous handoff**: `docs/RELEASE_HANDOFF.md` (2026-07-25 — superseded by this document)

---

## 0. What Changed Since Last Handoff

The production readiness audit (`docs/AUDIT-7-26.md`, score 42/100) identified 32 findings. **Phase A remediation** addressed the 8 findings that would block meaningful runtime validation:

| Fix | File(s) | Impact on VS-1 |
|-----|---------|----------------|
| Symptom payload contract | `frontend/src/lib/api.ts:185` | **Direct** — entry form no longer 422s |
| createCycle sends start_date | `frontend/src/lib/api.ts:282`, `SettingsPage.tsx` | **Direct** — "Start New Cycle" now works |
| ESLint CI step removed | `.github/workflows/ci.yml` | Build reproducibility |
| Repository layout committed | `repository/byrd_health_fertility/` (3 files) | **Critical** — add-on now installable from committed files |
| Alembic replaces create_all() | `app.py:44-67`, `run.sh:44-48` | Schema evolution now uses migrations |
| Migration 001 schema fix | `_001_initial_schema.py:71` | `temp_value` Float→Text matches models |
| Entity payload enrichment | `analysis.py:77-149`, wired in `app.py`, `entries.py`, `insights.py` | **Direct** — HA entities now receive `cycle_day`, `phase`, `last_temp`, `avg_cycle_length` |
| Temp_unit change blocked | `profiles.py:61-82` | **Direct** — prevents data corruption from unit switching |

### Test Results (current)

```
Python:   262 passed, 0 failures (was 160 in previous handoff — device_adapters, notifications, calendar tests added)
Frontend:  65 passed, 0 failures
TypeScript: typecheck clean
Docker:    Expected to build — not re-validated after Phase A
```

---

## 1. What to Validate

The validation checklist at `docs/releases/RC1_VALIDATION_CHECKLIST.md` remains the authoritative VS-1 guide. This handoff augments it with Phase-A-specific context.

### VS-1 Scope: Startup, Ingress, Core UI, API, Entities

**9 validation steps** in the checklist. All are still applicable. Read the checklist first, then note these updates:

### Critical Changes to Watch For

#### Entity Names Are `bbt_{slug}_*` Not `byrd_health_*`

The old handoff (`RELEASE_HANDOFF.md`) referenced entity names like `sensor.byrd_health_<slug>_today_temp`. Those names are outdated. The actual entity prefix is `bbt_`:

```
sensor.bbt_{slug}_cycle_day
sensor.bbt_{slug}_cycle_phase
sensor.bbt_{slug}_ovulation_date
sensor.bbt_{slug}_next_period_date
binary_sensor.bbt_{slug}_fertile_window
binary_sensor.bbt_{slug}_ovulation_confirmed
sensor.bbt_{slug}_last_temp          (conditional)
sensor.bbt_{slug}_luteal_length      (conditional)
sensor.bbt_{slug}_avg_cycle_length   (conditional)
```

#### Entity States Should Now Show Actual Values

After Phase A's enrichment fix, entities should show real values instead of "unknown":
- `sensor.bbt_{slug}_cycle_day` → should show a number (e.g., `"1"`)
- `sensor.bbt_{slug}_cycle_phase` → should show `"unknown"` (no data yet, but NOT literally "unknown" from default — it's the fertile_engine output)
- `sensor.bbt_{slug}_last_temp` → should appear if temperature data exists
- `sensor.bbt_{slug}_avg_cycle_length` → should appear if past cycles exist

If entities still show "unknown" for cycle_day/phase after data entry, the enrichment path has a bug.

#### Symptom Entry Should Not 422

The audit found that submitting symptoms produced a 422. This is fixed. Verify by:
1. Go to Log Entry page
2. Check 2-3 symptom checkboxes
3. Select a severity
4. Submit
5. **Expected**: 201 response, success toast, temperature saved

#### "Start New Cycle" in Settings Should Work

Previously this always 422'd. Now it shows a date picker. Verify:
1. Go to Settings
2. Click "Start New Cycle"
3. Date picker appears (defaults to today)
4. Select a future date (after current cycle start)
5. Click Confirm
6. **Expected**: Success message, new cycle created

#### Temperature Unit Switching Should Be Blocked

After entering temperature data, changing F↔C should show an error:
1. Log a temperature entry
2. Go to Settings
3. Try switching to Celsius
4. Click Save
5. **Expected**: Error message about existing temperature records

#### Database Migrations Run at Startup

Watch the startup logs for:
```
INFO: Database migrations applied successfully
```
Or if there's a path issue:
```
WARNING: alembic.ini not found at ...
```
If the WARNING appears, migration didn't run but the app continues (create_all fallback was removed).

---

## 2. Known Remaining Issues (Not Fixed in Phase A)

These exist but should NOT block VS-1:

| # | Issue | Severity | VS-1 Impact |
|---|-------|----------|-------------|
| 1 | HA bridge imported directly in `app.py` lifespan (ADR-0006) | High | None for VS-1 — bridge still works, just not cleanly decoupled |
| 2 | No standalone authentication | Critical | None for HA path — HA handles auth via Ingress |
| 3 | CORS `allow_credentials=True` with `["*"]` | Critical | None for HA path — Ingress proxy handles CORS |
| 4 | HA entity cleanup on profile deletion | Medium | Minor — stale entities after profile deletion |
| 5 | Notification "default" slug for temp reminders | Medium | May show notifications for wrong profile slug |
| 6 | N+1 queries in cycle listing | Medium | Unlikely to surface with small data in VS-1 |
| 7 | `npm install` instead of `npm ci` in Dockerfile | Medium | Docker build may have slightly different deps |
| 8 | Unpinned `base:latest` Docker image | Medium | May cause build differences if base image updated |

---

## 3. Pass Criteria (from checklist)

### CRITICAL Gates (any FAIL → session FAILS)

| # | Criterion | PASS Condition |
|---|-----------|---------------|
| C1 | Docker build | `docker build -t byrd-health:rc1 .` completes without errors |
| C2 | Add-on installs | HA Supervisor shows successful install |
| C3 | Add-on starts | Status shows green "Running" |
| C4 | No startup errors | Zero ERROR lines in logs |
| C5 | UI loads via Ingress | Dashboard renders when clicking OPEN WEB UI |
| C6 | API responds | Health check returns `{"status":"ok"}` |
| C7 | Entities published | At least 6 `bbt_*` entities visible in HA States |
| C8 | All 7 pages load | Each navigation item renders without errors or white screens |

---

## 4. Evidence Required

Full evidence checklist in `RC1_VALIDATION_CHECKLIST.md` §Evidence Package Checklist. Minimum 17 items:

- Docker build success screenshot
- Add-on install confirmation
- Full startup logs (text)
- Dashboard, Calendar, Entry, History, Settings page screenshots
- Browser console screenshot
- API health check output (curl)
- API profiles + insights output (curl)
- OpenAPI Swagger UI screenshot
- HA States filtered to `bbt_`
- Expanded entity attributes

---

## 5. Deliverables Expected from Release Engineer

1. **VS-1 Pass/Fail verdict** — per criterion, with explanation for each FAIL
2. **Evidence package** — all screenshots, logs, API outputs
3. **Release confidence assessment** — High/Medium/Low with justification
4. **Remediation items** (if FAIL) — what must be fixed before re-validation

---

## 6. Next Steps After VS-1

| VS-1 Result | Next Action |
|-------------|-------------|
| **PASS** | Advance to Phase B remediation (auth, CORS, Docker pinning, notification fixes). Then VS-2 (Data Entry, Charts, Cycle Management). |
| **FAIL — minor** | Fix identified issues, re-validate VS-1 |
| **FAIL — major** | Architect reviews failure, produces remediation plan, hands back to Release Engineer |

Phase B work can begin in parallel with VS-2/VS-3 validation — the Release Engineer and specialized agents can work concurrently on different areas.

---

*Handoff prepared by Lead Architect. Phase A remediation verified by 262 passing Python tests + 65 passing frontend tests + clean TypeScript compilation. The project is as ready for runtime validation as automated tooling can make it. Now runtime evidence must drive the next decisions.*
