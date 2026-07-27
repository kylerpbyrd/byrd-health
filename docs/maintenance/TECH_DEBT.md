# Technical Debt Register

> **Purpose:** Authoritative backlog for non-feature work. Prioritized by impact and effort.
> **Date:** 2026-07-26 | **Maintained by:** Lead Architect

---

## Priority Legend

| Priority | Definition |
|---|---|
| **P0 — Critical** | Security risk, data loss potential, or blocks a release |
| **P1 — High** | Significant maintenance burden, architectural drift, or CI gap |
| **P2 — Medium** | Code quality, documentation accuracy, developer experience |
| **P3 — Low** | Cosmetic, nice-to-have, future-proofing |

---

## P0 — Critical (0 items)

*No critical debt items currently block releases.*

---

## P1 — High

| ID | Item | Effort | Impact | Milestone | Owner |
|---|---|---|---|---|---|
| TD-001 | **Pin Docker base image.** Replace `FROM ghcr.io/home-assistant/base:latest` with digest or version tag. | S | Prevents non-deterministic builds and supply-chain risk | Phase 4 | DevOps |
| TD-002 | **Remove devDependencies from Docker image.** Use multi-stage build: build frontend in Node stage, copy static output to final Python stage. Cuts image size 30-50%. | M | Reduces attack surface, faster pulls, smaller footprint | Phase 4 | DevOps |
| TD-003 | **Add multi-arch Docker builds.** Add `linux/arm64` to CI platforms. Config claims 4 architectures; CI builds only amd64. | M | ARM users (Raspberry Pi) get nothing currently | Phase 4 | DevOps |
| TD-004 | **Add coverage reporting to CI.** Install `pytest-cov`, add `--cov` with threshold (80%), upload artifact. | S | Visibility into untested code paths | Phase 4 | QA |
| TD-005 | **Add `pip-audit` / dependency scanning to CI.** Zero vulnerability scanning for a health data platform. | S | Catch CVEs before they reach production | Phase 4 | Security |
| TD-006 | **Fix 5 Graphify entity node key_fields.** `cycle`, `temperature-record`, `fertility-signs`, `computed-insights`, `symptom` nodes have wrong field names vs actual SQLAlchemy models. | S | Graphify is inaccurate — violates "stale Graphify is a defect" | M4 | Graphify |
| TD-007 | **Consolidate duplicate IngressMiddleware.** Both `ha_bridge/ingress.py` and `web_api/ingress.py` implement the same ASGI middleware. Only `web_api/ingress.py` is used in production. | S | Maintenance burden, potential divergence | M4 | Backend |
| TD-008 | **Consolidate duplicate schemas.** `data_service/schemas.py` and `web_api/schemas/responses.py` have 6 overlapping schema classes with subtle differences. | M | Schema drift risk, confusing for new contributors | Phase 4 | Backend |
| TD-009 | **Align pre-commit and CI strictness.** Pre-commit mypy runs `--strict`; CI mypy does not. Pre-commit format check; CI does not. | S | Developer confusion; format violations can reach main | M4 | DevOps |
| TD-010 | **Investigate C8 dashboard indicator.** Dashboard shows "Offline" despite WebSocket connecting via Ingress. React hook's `isConnected` state may not propagate to UI. | M | Live dashboard feature is non-functional for users | Phase 4 | Frontend |

---

## P2 — Medium

| ID | Item | Effort | Impact | Milestone | Owner |
|---|---|---|---|---|---|
| TD-011 | **Fix 9 broken `LEGACY_REVIEW.md` references.** 8 ADRs + PROMPT.md reference `docs/LEGACY_REVIEW.md` which moved to `docs/archive/`. | S | Broken cross-document links | M4 | Docs |
| TD-012 | **Archive 10 obsolete documents.** RELEASE_HANDOFF, SESSION_HANDOFF, MILESTONE_GUIDE, PHASE3_PLAN, RELEASE_CANDIDATE_VALIDATION, RUNTIME_READINESS_REPORT, RC1_RUNTIME_VALIDATION, PROJECT_IDEA, PROMPT.md (+ legacy equivalents). | S | Conflicting versions confuse contributors | M4 | Docs |
| TD-013 | **Remove duplicate test files.** `test_regression.py` (100% duplicate), `test_protocol.py` (tests Python isinstance, not app logic). | S | Maintenance burden, false confidence | M4 | QA |
| TD-014 | **Standardize async test patterns.** `test_devices.py` and `test_websocket.py` use sync `TestClient`; all other web_api tests use `httpx.AsyncClient`. `test_bluetooth.py` uses `asyncio.run()` inside sync functions. | S | Fragile tests, confusing patterns | Phase 4 | QA |
| TD-015 | **Fix timing-dependent tests.** `test_poller.py` and `test_ha_sensor.py` use `asyncio.sleep(0.05)` which will flake in CI under load. | S | CI instability | Phase 4 | QA |
| TD-016 | **Add missing ADR-0013 row to README.md and ARCHITECTURE.md.** Both say "12 ADRs"; actual count is 13. | S | Documentation accuracy | M4 | Docs |
| TD-017 | **Update README phase status.** Says "Phase 2 — Production Release Candidate"; Phase 3 is complete. | S | Misleading to new contributors | M4 | Docs |
| TD-018 | **Fix ADR-0011 endpoint mismatch.** ADR documents `POST /api/v1/fertility/devices/{id}/read`; implementation uses `POST /api/v1/fertility/devices/read`. | S | ADR-impl drift | Phase 4 | Backend |
| TD-019 | **Fix ADR-0008 encryption claim.** ADR says "HKDF key derivation"; implementation uses plain SHA-256. Update ADR to match reality. | S | Inaccurate security documentation | Phase 4 | Security |
| TD-020 | **Create 18 missing Graphify node files.** 7 entities, 1 function, 1 milestone, 9 documents have index entries but no backing JSON files. | M | Graphify completeness | M4 | Graphify |
| TD-021 | **Remove `estimate_baseline()` or integrate it.** Function exists, is tested, but has zero production callers. | S | Dead code carrying test burden | M4 | Backend |
| TD-022 | **Remove `DashboardResponse` schema.** Pydantic model defined in `responses.py` but no route returns it and no frontend consumes it. | S | Dead code | M4 | Backend |
| TD-023 | **Remove unused router export aliases.** `routers/__init__.py` exports 7 named router aliases that are never imported. | S | Dead code | M4 | Backend |

---

## P3 — Low

| ID | Item | Effort | Impact | Milestone | Owner |
|---|---|---|---|---|---|
| TD-024 | **Standardize optional-deps naming.** Some use `[dev]`, others `[test]`. | S | Consistency | Phase 4 | Backend |
| TD-025 | **Standardize pytest-asyncio version.** `>=0.23` in some packages, `>=0.24` in others. | S | Consistency | Phase 4 | QA |
| TD-026 | **Fix reversed timestamps in 4 Graphify nodes.** `created_at > updated_at` on adr-0011, adr-0012, session-handoff, phase3-plan. | S | Data integrity | M4 | Graphify |
| TD-027 | **Rename `FertilitySigns` model to `FertilitySign`.** All other SQLAlchemy models use singular naming. | S | Consistency | Phase 4 | Database |
| TD-028 | **Rename `ComputedInsights` to `ComputedInsight`.** Same singular naming inconsistency. | S | Consistency | Phase 4 | Database |
| TD-029 | **Add `ha-bridge` to web_api pyproject.toml dependencies.** `app.py` imports from ha_bridge directly but it's not declared (works transitively via device-adapters). | S | Explicit dependency | M4 | Backend |
| TD-030 | **Add Python lock file (`requirements.lock`).** No deterministic dependency resolution for Docker builds. | S | Reproducible builds | Phase 4 | DevOps |
| TD-031 | **Add `HEALTHCHECK` and non-root user to Dockerfile.** Security and operational best practice. | S | Container health | Phase 4 | DevOps |
| TD-032 | **Remove `legacy/tests/`.** Tests legacy Flask app superseded by FastAPI rewrite. | S | Maintenance burden | M4 | QA |
| TD-033 | **Remove `frontend/src/lib/mock-data.ts`.** 287 lines, zero consumers. | S | Dead code | M4 | Frontend |
| TD-034 | **Mark `legacy/` as archival.** Add README noting it's historical reference only. | S | Clarity for new contributors | M4 | Docs |

---

## Summary

| Priority | Count |
|---|---|
| P0 — Critical | 0 |
| P1 — High | 10 |
| P2 — Medium | 13 |
| P3 — Low | 11 |
| **Total** | **34 items** |

**P1 items recommended for Phase 4:** 8 items (TD-001 through TD-005, TD-008, TD-010, TD-014)

**Quick wins (M4):** TD-006, TD-007, TD-009 through TD-013, TD-016, TD-017, TD-020, TD-021, TD-022, TD-023, TD-026, TD-029, TD-032 through TD-034 (19 items, all estimated S effort)
