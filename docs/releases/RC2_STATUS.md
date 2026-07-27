# RC2 Status Update

> **Date:** 2026-07-26 | **Current Gate:** M1 — Phase 4A Complete (APPROVED WITH CONDITIONS)  
> **Previous Report:** `docs/releases/RC2_READINESS.md`

---

## RC2 Gate Progression

```
Development ──> RC1 (VS-1 PASS) ──> Phase 3.5 ──> Phase 4A (M1) ──> Phase 4B (M2)
                                                                        │
                                                                   CURRENT POSITION
```

---

## Metrics Tracker

| Metric | RC1 | Phase 4A (Current) | RC2 Target | Delta to Target |
|---|---|---|---|---|
| Python tests | 255 | 285 | 350+ | -65 |
| Packages | 5 | 6 | 7+ | -1 |
| HA entities | 9 | 9 | 12+ | -3 |
| REST endpoints | 16 | 19 | 22+ | -3 |
| Frontend pages | 7 | 8 | 10+ | -2 |
| WebSocket types | 2 active | 2 active | 3 active (+heartbeat) | -1 |
| Docker architectures | 1 (amd64) | 2 (amd64+arm64) | 2 | ✅ DONE |
| Graphify nodes | 83 | 89 | 100+ | -11 |
| Graphify accuracy | 100% | 99% (1 false edge) | 100% | -1 fix |
| Known issues | 2 | 2 | ≤ 3 | On track |
| VS validation | VS-1 PASS | VS-1 PASS | VS-3 PASS | VS-2 + VS-3 pending |
| Documentation completeness | 9/10 | 9/10 | 9/10 | ✅ |

---

## Known Issues (Current)

| ID | Issue | Severity | Status |
|---|---|---|---|
| C1 | False Graphify edge: pregnancy-engine → data-service | High | Fix before Phase 4B |
| C2 | PregnancyPage uses raw fetch instead of React Query | Medium | Fix before Phase 4B |

---

## Phase 4A Resolved Issues

| Issue | Resolution |
|---|---|
| C8 dashboard indicator (TD-010) | FIXED — stale closure in useCallback was causing perpetual connect/disconnect loop |
| Schema duplication (TD-008) | RESOLVED — 6 Pydantic classes consolidated to data_service |
| ADR-0011 endpoint mismatch (TD-018) | RESOLVED — ADR updated with implementation note |
| ADR-0008 encryption claim (TD-019) | RESOLVED — ADR updated to reflect SHA-256 |
| Multi-arch Docker (TD-003) | RESOLVED — amd64 + arm64 in CI |

---

## Next Gate: M2 (Phase 4B Complete)

### Prerequisites for M2

| # | Item | Owner |
|---|---|---|
| 1 | C1 fixed (Graphify edge) | Graphify Engineer |
| 2 | C2 fixed (React Query refactor) | Frontend Engineer |
| 3 | Pregnancy router OpenAPI responses (C4) | Backend Engineer |

### M2 Criteria (from MILESTONES.md)

1. Symptom catalog seeded ✅
2. Medication model exists
3. Symptom catalog API works
4. Medication API works
5. Structured symptom picker
6. Medication log UI
7. HA entities updated
8. WebSocket heartbeat active
9. Graphify updated
10. Full test suite passes

---

## Risk Assessment

| Risk | Current Status | Trend |
|---|---|---|
| React Query pattern divergence spreads to Phase 4B | Mitigated — C2 fix required before Phase 4B | ✅ |
| Backend Engineer bottleneck slows Phase 4B | Same as Phase 4A — BE has 4 tasks in Phase 4B | → Stable |
| New modules increase frontend bundle | PregnancyPage added — no measurable increase | → Stable |
| Community Store submission delayed | Branding assets ready (SVG placeholder). Multi-arch done. | ↓ Improving |

---

## Release Confidence

| Factor | Confidence | Notes |
|---|---|---|
| Architecture stability | High | Zero boundary violations, clean dependency graph |
| Test coverage | Medium | 285 tests, no coverage metric. Should reach 80% by RC2. |
| Frontend quality | Medium | Pattern divergence (C2) must be fixed before new pages |
| CI/CD maturity | Medium | Multi-arch done. No coverage reporting. No security scanning. |
| Documentation | High | ADRs accurate. OpenAPI partial (pregnancy router missing). ARCHITECTURE updated. |
| **Overall** | **Medium-High** | Architecture is strong. Operational maturity (coverage, CI, frontend patterns) needs Phase 4B attention. |

---

RC2 remains on track for Phase 4D completion. No blockers identified that would delay the release beyond the planned timeline.
