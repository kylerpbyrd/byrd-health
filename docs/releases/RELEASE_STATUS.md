# Release Status — Byrd Health v2.0.0

> **Release Engineer:** Independent certification
> **Date:** 2026-07-26
> **Current Gate:** RC1 → VS-1 Runtime Validation (HANDED OFF)
> **Target Gate:** Production (Home Assistant Community)
> **Phase A Audit Remediation:** COMPLETE

---

## Current Status: HANDED OFF TO RELEASE ENGINEER — AWAITING VS-1 EVIDENCE

RC1 passes all automated checks (262 Python tests, 65 frontend tests, clean typecheck). Phase A audit remediation resolved 8 critical/high findings. The release cannot advance until VS-1 runtime validation on a live Home Assistant instance is completed and evidence is reviewed.

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

---

## Current Status: GATED — AWAITING RUNTIME VALIDATION

RC1 passes all automated checks (code audit, unit tests, Docker build). The release cannot advance until runtime validation on a live Home Assistant instance is completed and evidence is reviewed.

---

## Gate Progression

| Gate | Status | Date | Verdict |
|------|--------|------|---------|
| **Development** | Complete | 2026-07-25 | — |
| **RC0** | Complete | 2026-07-25 | PASS |
| **RC1 — Audit** | Complete | 2026-07-26 | Phase A remediation complete |
| **RC1 — VS-1** | **HANDED OFF** | 2026-07-26 | AWAITING RELEASE ENGINEER |
| **Beta** | Not Started | — | — |
| **Release Candidate** | Not Started | — | — |
| **Production** | Not Started | — | — |

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
| **HA Runtime** | **LOW** | No runtime evidence — VS-1 not yet executed |
| **Production** | **LOW** | Requires HA runtime evidence before any production claim |

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
| **VS-1** | Startup, Ingress, Core UI, API, Entities | **READY** | RC1_VALIDATION_CHECKLIST.md |
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

**User must complete Validation Session 1 (VS-1)** per `RC1_VALIDATION_CHECKLIST.md`.

Evidence required: screenshots, logs, entity state snapshots, API responses.

Release Engineer will analyze evidence and produce PASS/FAIL verdict.

**Do not proceed to Phase 3 implementation until RC1 Runtime Validation passes.**

---

*This document updates with each validation session verdict.*
