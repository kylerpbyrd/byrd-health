# RC2 Readiness Assessment

> **Date:** 2026-07-26 | **Current Release:** RC1 (VS-1 PASS)  
> **Target:** RC2 — Phase 4 Complete

---

## Current State

| Metric | RC1 | RC2 Target |
|---|---|---|
| Python tests | 255 | 350+ |
| Packages | 5 | 7+ |
| HA entities | 9 per profile | 12+ per profile |
| REST endpoints | 16 | 20+ |
| Frontend pages | 7 | 10+ |
| WebSocket message types | 2 active | 3 active (+ heartbeat) |
| Docker architectures | amd64 only | amd64 + arm64 |
| Graphify nodes | 83 | 95+ |
| Coverage | unknown | ≥ 80% |
| VS validation | VS-1 PASS, VS-2 partial | VS-1 through VS-3 PASS |

---

## RC2 Prerequisites

| # | Item | Status | Blocks |
|---|---|---|---|
| 1 | PREQ-1: Frontend WS contract alignment | Pending | M1 |
| 2 | PREQ-2: Multi-arch Docker builds | Pending | M5 |
| 3 | PREQ-3: C8 dashboard indicator | Pending | M1 |

---

## RC2 Validation Plan

### VS-3: Phase 4 Feature Validation

Extends VS-2 with new scenarios:

| Check | Description |
|---|---|
| VS3-C1 | Pregnancy dashboard renders |
| VS3-C2 | Create pregnancy from cycle |
| VS3-C3 | Symptom catalog picker replaces free-text |
| VS3-C4 | Medication log entry works |
| VS3-C5 | Sleep entry and chart render |
| VS3-C6 | Nutrition meal logger works |
| VS3-C7 | Cross-module insight visible (sleep by cycle phase) |
| VS3-C8 | Cycle explanation text appears |
| VS3-C9 | Multi-profile works with new modules |
| VS3-C10 | Cleanup all test data |

### VS-4: Production Readiness (future)

| Check | Description |
|---|---|
| VS4-C1 | Docker multi-arch pull and run |
| VS4-C2 | HA restart recovery |
| VS4-C3 | Backup and restore |
| VS4-C4 | Upgrade from RC1 to RC2 |
| VS4-C5 | 7-day continuous runtime |

---

## RC2 Release Checklist

- [ ] All 6 milestone gates cleared (M0-M5)
- [ ] 350+ tests passing, 0 failures
- [ ] Multi-arch Docker images on GHCR
- [ ] CHANGELOG v2.2.0 written
- [ ] VS-3 executed and PASS
- [ ] HA Community Store compliance verified
- [ ] Known issues documented in `KNOWN_ISSUES.md`
- [ ] Graphify 100% accurate
- [ ] README, ARCHITECTURE, USER_GUIDE updated
- [ ] Release Engineer certification

---

## Risk Factors for RC2

| Risk | Mitigation |
|---|---|
| Schema consolidation breaks existing API responses | Run full test suite after 4A.1. Test API responses match frontend expectations. |
| Pregnancy engine date math has edge cases (IVF, irregular cycles) | Test with known good dates. Get medical review if possible. |
| Nutrition food database scope creep | Limit to manual entry for RC2. Defer food database to Phase 5. |
| Sleep time-series data causes chart performance issues | Test with 30+ days of data. Paginate if needed. |
| ARM Docker builds time out in CI | Use QEMU caching. Accept slower builds initially. |
