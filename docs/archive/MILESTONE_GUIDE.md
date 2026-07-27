# Milestone Guide — Byrd Health

> Based on full project audit. Date: 2026-07-26

---

## Current State: Phase 1 Complete, Phase 2 ~60% Complete

The platform foundation is solid. The add-on deploys, the page renders, and the API works. But several Phase 2 milestones are incomplete or not wired up.

---

## Priority Triage

### Critical (add-on not fully functional without these)

| # | Issue | Milestone |
|---|-------|-----------|
| 1 | HA Bridge not wired into web_api — entity publishing dead code | P2-M1.7 |
| 2 | Dashboard BBT chart uses hardcoded mock data, not real API | P2-M5.1 |
| 3 | No encryption at rest — health data stored in plaintext SQLite | P2-M4 |

### High (user-visible gaps)

| # | Issue | Milestone |
|---|-------|-----------|
| 4 | "Today's Signs" card shows hardcoded values | P2-M5.1 |
| 5 | No error boundaries or toast notifications in frontend | P2-M5.3 |
| 6 | No WebSocket endpoint (documented in architecture, not implemented) | Phase 3 |
| 7 | No user-facing documentation (install guide, feature docs) | P2-M6.4 |

### Medium (quality / tooling)

| # | Issue | Milestone |
|---|-------|-----------|
| 8 | pytest fails collection from root (conftest naming conflict) | M1.4 |
| 9 | No Docker build or coverage reporting in CI | M1.3 |
| 10 | Legacy migration tool has no DB writer (JSON output only) | P2-M3.4 |
| 11 | Empty docs directories (decisions/, architecture/, research/) | cleanup |

### Low

| # | Issue | Milestone |
|---|-------|-----------|
| 12 | Flaky test: test_delete_profile (ordering issue) | M4.8 |
| 13 | Frontend test coverage limited (21 tests, 3 files) | M5.10 |

---

## Milestone Roadmap

### M-A: Immediate Fixes (estimated: 1 session)

**Objective:** Fix bugs in currently deployed add-on. No new features.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-A.1 | Replace mock chart data with real API data | Frontend Engineer | `DashboardPage.tsx` | Dashboard BBT chart shows real cycle data |
| M-A.2 | Wire "Today's Signs" to real API | Frontend Engineer | `DashboardPage.tsx` | Mucus/OPK values from live data |
| M-A.3 | Fix conftest naming conflict | Backend Engineer | Rename `tests/conftest.py` files | `pytest` from root passes |
| M-A.4 | Clean empty docs directories | Architect | `docs/decisions/`, `docs/architecture/`, `docs/research/` | Removed |
| M-A.5 | Add Docker build step to CI | DevOps Engineer | `.github/workflows/ci.yml` | Docker build validates on PR |

---

### M-B: HA Bridge Wiring (estimated: 2 sessions)

**Objective:** Wire the HA Bridge into the running application so entities are published.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-B.1 | Add HA Bridge lifespan hook to web_api | Backend Engineer | `app.py`, `dependencies.py` | Bridge starts on app startup, publishes entities |
| M-B.2 | Wire entity publishing after cycle analysis | Backend Engineer | `routers/entries.py`, `analysis.py` | After entry is created, entities update |
| M-B.3 | Add entity publishing on startup | Backend Engineer | `app.py` lifespan | All 9 entities registered on boot |
| M-B.4 | Write integration tests for HA Bridge wiring | QA Engineer | `tests/integration/` | Mock HA API verifies publish calls |

**ADR-0006 note:** The HA Bridge MUST remain the only component with HA imports. The wiring in web_api uses the `HABridgeProtocol` interface, not the concrete implementation.

---

### M-C: Encryption at Rest (estimated: 2 sessions)

**Objective:** Encrypt sensitive health data per ADR-0008.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-C.1 | Implement AES-256-GCM encryption module | Security Engineer | `data_service/encryption.py` | Encrypt/decrypt round-trip |
| M-C.2 | Add per-profile key management | Security Engineer | `data_service/encryption.py` | Keys derived from profile UUID + SECRET_KEY |
| M-C.3 | Encrypt temperature values, signs, symptoms | Security Engineer | `data_service/models.py`, `repositories.py` | Sensitive columns encrypted at rest |
| M-C.4 | Add encryption to export | Security Engineer | `routers/profiles.py` | Exported JSON has encrypted fields |
| M-C.5 | Write encryption tests | QA Engineer | `tests/test_encryption.py` | Round-trip, key rotation, tamper detection |

**Risk:** Encrypting existing data requires a migration path. Deploy to fresh installs first.

---

### M-D: Frontend Polish (estimated: 2 sessions)

**Objective:** Improve UI quality — error handling, loading states, accessibility.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-D.1 | Add ErrorBoundary component | Frontend Engineer | `components/ErrorBoundary.tsx` | Catches render errors gracefully |
| M-D.2 | Add toast notifications | Frontend Engineer | Install sonner or react-hot-toast | Success/error toasts on mutations |
| M-D.3 | Replace spinners with skeleton loaders | Frontend Engineer | All page components | Content-placeholder skeletons during load |
| M-D.4 | Improve empty states | Frontend Engineer | `DashboardPage`, `HistoryPage` | Friendly messages when no data exists |
| M-D.5 | Accessibility audit | Frontend Engineer | All components | Lighthouse ≥ 90, keyboard navigation |
| M-D.6 | Expand test coverage | QA Engineer | All page components | ≥50 tests, critical paths covered |

---

### M-E: Documentation & Release Prep (estimated: 2 sessions)

**Objective:** Prepare for public release.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-E.1 | User installation guide | Doc Engineer | `docs/USER_GUIDE.md` | Step-by-step HA add-on install |
| M-E.2 | Feature documentation | Doc Engineer | `docs/FEATURES.md` | Sympto-thermal method explained |
| M-E.3 | API reference | Backend Engineer | Auto-generated OpenAPI | `/docs` endpoint accessible |
| M-E.4 | Troubleshooting guide | Doc Engineer | `docs/TROUBLESHOOTING.md` | Common issues + solutions |
| M-E.5 | Changelog | Architect | `CHANGELOG.md` | Version history |
| M-E.6 | End-to-end deployment test | QA Engineer | Full HA install flow | Clean install → profile → entries → dashboard |
| M-E.7 | Security review | Security Engineer | Dependency audit, threat model | No critical vulnerabilities |
| M-E.8 | Performance baseline | QA Engineer | Benchmark script | Cycle analysis < 500ms, API responses < 100ms |

---

### M-F: Legacy Migration Completion (estimated: 1 session)

**Objective:** Complete the migration tool so legacy users can move their data.

| Task | Agent | Files | Acceptance |
|---|---|---|---|
| M-F.1 | Implement DB writer for migration | Backend Engineer | `tools/legacy-migrate/writer.py` | Inserts into new database |
| M-F.2 | Add end-to-end migration test | QA Engineer | `tools/legacy-migrate/tests/` | Sample legacy DB → new DB verified |
| M-F.3 | Add dry-run mode validation | Backend Engineer | `tools/legacy-migrate/migrate.py` | Preview without writing |

---

### M-G: Phase 3 Scoping (estimated: 1 session)

**Objective:** Plan device integrations and WebSocket architecture. No implementation.

| Task | Agent | Deliverables |
|---|---|---|
| M-G.0 | Research Bluetooth thermometer APIs | Architect | `docs/research/bt-thermometers.md` |
| M-G.1 | Draft Phase 3 plan | Architect | `docs/PHASE3_PLAN.md` |
| M-G.2 | Create ADR-0011 (Device Adapter Pattern) | Architect | `docs/adr/ADR-0011-device-adapter-pattern.md` |
| M-G.3 | Create ADR-0012 (WebSocket Architecture) | Architect | `docs/adr/ADR-0012-websocket-architecture.md` |
| M-G.4 | Scope ESPHome integration | Architect | `docs/research/esphome-integration.md` |

---

## Execution Order

```
M-A (Immediate Fixes) ────────────────────── 1 session
  │
  ├──► M-B (HA Bridge Wiring) ─────────────── 2 sessions
  │       │
  │       ▼
  ├──► M-C (Encryption) ───────────────────── 2 sessions
  │
  ├──► M-D (Frontend Polish) ──────────────── 2 sessions  (parallel with M-B/M-C)
  │
  ├──► M-E (Documentation & Release) ──────── 2 sessions  (after M-B, M-C, M-D)
  │
  ├──► M-F (Legacy Migration) ─────────────── 1 session   (parallel with M-E)
  │
  └──► M-G (Phase 3 Scoping) ──────────────── 1 session   (parallel with M-F)
```

**Total: ~8 sessions** to reach a production-quality HA add-on ready for public release.

---

## Quick Wins (can be done in 1 session)

If you want to see progress fast, do M-A:

- Fix the dashboard chart bug (real data instead of mock)
- Wire "Today's Signs" to real API
- Fix pytest root collection
- Add Docker build to CI

These are all low-risk, high-visibility fixes that make the add-on feel complete.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Encryption breaks existing data | Medium | High | Deploy to fresh installs first; add migration path |
| HA Bridge entity publishing conflicts with existing sensors | Low | Medium | Namespace entities by profile slug |
| Skeleton loaders add bundle size | Low | Low | Lazy-load skeleton components |
| Legacy migration writer corrupts data | Medium | High | Dry-run mode; backup before migration |
| Phase 3 device integrations require hardware | High | Low | Start with simulated devices; test with real hardware later |

---

## Agent Assignments by Milestone

| Milestone | Primary Agent | Supporting Agents |
|---|---|---|
| M-A | Frontend Engineer | Backend Engineer, DevOps Engineer |
| M-B | Backend Engineer | HA Engineer, QA Engineer |
| M-C | Security Engineer | Database Engineer, QA Engineer |
| M-D | Frontend Engineer | QA Engineer |
| M-E | Documentation Engineer | QA Engineer, Security Engineer |
| M-F | Backend Engineer | QA Engineer |
| M-G | Architect | — |
