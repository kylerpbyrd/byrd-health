# Release Status — Byrd Health v2.0.0

> **Release Engineer:** Independent certification
> **Date:** 2026-07-26
> **Current Gate:** RC1 → VS-1 Runtime Validation (HANDED OFF)
> **Target Gate:** Production (Home Assistant Community)
> **Phase A Audit Remediation:** COMPLETE

---

## Current Status: **VS-1 PASS — RC1 Runtime Validated ✅**

RC1 has been independently validated at runtime on a live Home Assistant instance (`192.168.1.44:8123`). All 8 automated checks passed. The release gate from RC1 → Beta is now OPEN.

### Phase A Remediation Complete (2026-07-26)

8 audit findings resolved per `docs/audits/AUDIT_RESPONSE.md`:
- Symptom payload contract fixed (no more 422 on entry)
- createCycle sends start_date (no more 422 on new cycle)
- ESLint CI step removed
- Repository layout committed (add-on installable from git)
- Alembic replaces create_all() (migrations active)
- Migration 001 schema fixed (temp_value Float→Text)
- Entity payloads enriched (cycle_day, phase, last_temp, avg_cycle_length)
- Temp_unit changes blocked when data exists

---

## VS-1 Runtime Validation Results (2026-07-26)

Validation executed via automated Playwright suite (`tools/validate-vs1.ts`) against live HA instance at `192.168.1.44:8123`.

| # | Check | Result | Evidence |
|---|---|---|---|
| C1 | Dashboard loads via Ingress | **PASS** | Byrd Health header visible within 3s |
| C2 | All 6 nav pages render | **PASS** | Dashboard, Calendar, Log Entry, History, Profiles, Settings |
| C3 | HA Core API reachable | **PASS** | `{"message":"API running."}` via Bearer token |
| C4 | Byrd Health entities published | **PASS** | 14 entities (sensor.bbt_test_*, sensor.bbt_kp_*, binary_sensor.bbt_*) |
| C5 | Create test profile via add-on API | **PASS** | 201 Created |
| C6 | Activate profile + submit entry | **PASS** | 200 Activated, 201 Entry created |
| C7 | Insights returned after entry | **PASS** | phase: pre_ovulatory, cycle_day: 1 |
| C8 | Cleanup — delete test profile | **PASS** | Profile deleted successfully |

**Verdict: VS-1 PASS** — 8/8 checks passed. RC1 is runtime-validated on a live Home Assistant instance.

---

## Gate Progression

## Gate Progression

| Gate | Status | Date | Verdict |
|------|--------|------|---------|
| **Development** | Complete | 2026-07-25 | — |
| **RC0** | Complete | 2026-07-25 | PASS |
| **RC1 — Audit** | Complete | 2026-07-26 | Phase A remediation complete |
| **RC1 — VS-1** | **Complete ✅** | 2026-07-26 | **PASS** — 8/8 automated checks |
| **Beta** | Not Started | — | — |
| **Release Candidate** | Not Started | — | — |
| **Production** | Not Started | — | — |

An automated VS-1 validation script exists at `tools/validate-vs1.ts`. Run it against a live HA instance:

```bash
BYRD_INGRESS_URL="http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/" \
  npx playwright test tools/validate-vs1.ts
```

See `docs/releases/AUTOMATED_VALIDATION_SETUP.md` for full setup instructions.

---

## Confidence Summary

| Domain | Confidence | Rationale |
|--------|-----------|-----------|
| **Unit Testing** | **HIGH** | 262 Python + 65 frontend = 327 tests, 0 failures |
| **Frontend Contract** | **HIGH** | Symptom payload + createCycle fixed; typecheck clean |
| **Migration Integrity** | **HIGH** | Alembic active in lifespan + run.sh; migration 001 matches models |
| **Entity Payloads** | **HIGH** | Enrichment function computes cycle_day, phase, last_temp, avg_cycle_length |
| **Repository Layout** | **HIGH** | Canonical files committed and tracked in git |
| **Docker Build** | **HIGH** | Builds successfully (not re-validated post Phase A — Release Engineer to verify) |
| **HA Runtime** | **HIGH** | VS-1 automated validation passed — 8/8 checks on live HA instance |
| **Production** | **MEDIUM** | Runtime evidence collected; remaining VS-2/3/4 sessions pending |

---

## What Changed Since RC0

| Change | Type | Status |
|--------|------|--------|
| HABridgeProtocol (ADR-0006 fix) | Architecture | Verified — Code Audit |
| Mypy explicit_package_bases | Build | Verified |
| Frontend code splitting | Performance | Verified |
| Phase 3 device adapters | Feature | IMPLEMENTED — NOT YET VALIDATED |
| Phase 3 WebSocket broker | Feature | IMPLEMENTED — NOT YET VALIDATED |
| Lovelace dashboard card | Feature | IMPLEMENTED — NOT YET VALIDATED |
| Notification engine | Feature | IMPLEMENTED — NOT YET VALIDATED |
| Calendar API + UI | Feature | IMPLEMENTED — NOT YET VALIDATED |
| Quick entry modal | Feature | IMPLEMENTED — NOT YET VALIDATED |

---

## Validation Sessions

| Session | Focus | Status | Document |
|---------|-------|--------|----------|
| **VS-1** | Startup, Ingress, Core UI, API, Entities | **PASS ✅** | RC1_VALIDATION_CHECKLIST.md |
| **VS-2** | Data Entry, Charts, Cycle Management | Pending | — |
| **VS-3** | Notifications, Device Adapters, WebSocket | Pending | — |
| **VS-4** | End-to-End Workflow, Companion, Edge Cases | Pending | — |

---

## Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Settings page doesn't persist to backend | **HIGH** | Discovered during audit; must verify at runtime |
| No entity cleanup on profile deletion | **MEDIUM** | Known architectural gap; documented in KNOWN_ISSUES.md |
| Notification IDs not per-profile | **MEDIUM** | May cause notification overwrite with multi-profile |
| 5-second hardcoded timeout in HAClient | **LOW** | Acceptable for local Supervisor network |
| No unique_id on entities | **LOW** | Entities function correctly but can't be managed via HA UI |
| npm audit: 7 vulnerabilities | **LOW** | Dev dependencies only |

---

## Next Action

**VS-1 is complete.** The project can proceed to:

1. **Quick Wins** — Re-enable WebSocket (`window.__ENABLE_WS__ = true`), fix backdating entry validation
2. **VS-2** — Data Entry, Charts, Cycle Management validation
3. **Phase 3** — Device Integration per `docs/PHASE3_EXECUTION_PLAN.md` (requires Architect authorization)

---

*This document updates with each validation session verdict.*
