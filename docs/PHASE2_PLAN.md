# Phase 2 Implementation Plan — Fertility Product Features

> Status: Ready for execution | Date: 2026-07-23 | Phase 1: Complete

---

## 1. Phase 2 Overview

**Objective:** Transform the Phase 1 platform foundation into a deployable Home Assistant Add-on with full fertility product features and HA integration.

**Exit Criteria:**
- HA Bridge publishes all 9 entities per profile
- HA Add-on packages and deploys successfully
- Legacy data migration tool is functional
- Data encryption is implemented at rest
- Frontend is fully connected to real API (mock fallback removed)
- Platform runs end-to-end on a Home Assistant instance

---

## 2. Milestones

### P2-M1: HA Bridge Service
**Complexity:** Medium | **Dependencies:** Phase 1 core platform

The HA Bridge is the ONLY component with Home Assistant dependencies. It isolates all HA-specific logic per ADR-0006.

| Task | Agent | Deliverables |
|---|---|---|
| P2-M1.1 | Create `packages/ha_bridge/` package scaffold | HA Engineer | pyproject.toml, src structure |
| P2-M1.2 | Implement entity publishing | HA Engineer | POST to HA REST API `/states/{entity_id}` |
| P2-M1.3 | Implement sensor polling | HA Engineer | GET from HA REST API with configurable interval |
| P2-M1.4 | Implement Ingress path handling | HA Engineer | X-Ingress-Path header middleware |
| P2-M1.5 | Implement config translation | HA Engineer | bashio → internal settings model |
| P2-M1.6 | Implement startup entity registration | HA Engineer | Register all entities on add-on start |
| P2-M1.7 | Write HA Bridge tests | QA Engineer | Mock HA API; verify entity publishing |

### P2-M2: HA Add-on Packaging
**Complexity:** Low | **Dependencies:** P2-M1

| Task | Agent | Deliverables |
|---|---|---|
| P2-M2.1 | Create `config.yaml` | HA Engineer | Add-on metadata, options schema, Ingress config |
| P2-M2.2 | Create `Dockerfile` | DevOps Engineer | Multi-stage build (Python + frontend), HA base image |
| P2-M2.3 | Create `run.sh` | DevOps Engineer | bashio config reading, uvicorn startup |
| P2-M2.4 | Update CI for add-on validation | DevOps Engineer | YAML lint, Docker build, add-on structure check |
| P2-M2.5 | Create `repository.yaml` | HA Engineer | Repository metadata for HA Add-on Store |

### P2-M3: Legacy Data Migration
**Complexity:** Medium | **Dependencies:** Phase 1 core platform (data_service)

| Task | Agent | Deliverables |
|---|---|---|
| P2-M3.1 | Create migration utility scaffold | Backend Engineer | `tools/legacy-migrate/` with reader/transformer/writer |
| P2-M3.2 | Implement legacy DB reader | Backend Engineer | Read old `bbt.db` schema, extract data |
| P2-M3.3 | Implement data transformer | Backend Engineer | Integer→UUID mapping, schema remapping |
| P2-M3.4 | Implement new DB writer | Backend Engineer | Insert via data_service API, validation |
| P2-M3.5 | Add dry-run and validation mode | Backend Engineer | Preview migration without writing |
| P2-M3.6 | Write migration tests | QA Engineer | Test with sample legacy database |

### P2-M4: Data Encryption
**Complexity:** Medium | **Dependencies:** P2-M1

| Task | Agent | Deliverables |
|---|---|---|
| P2-M4.1 | Implement AES-256-GCM encryption | Security Engineer | `data_service/encryption.py` |
| P2-M4.2 | Add per-profile key management | Security Engineer | Key derivation, encrypted key storage |
| P2-M4.3 | Encrypt sensitive columns | Security Engineer | Temperature values, fertility signs, symptoms |
| P2-M4.4 | Add encryption to export/backup | Security Engineer | Encrypted JSON exports |
| P2-M4.5 | Write encryption tests | QA Engineer | Encryption/decryption round-trip, key rotation |

### P2-M5: Frontend-Backend Integration
**Complexity:** Low | **Dependencies:** P2-M1, P2-M2

| Task | Agent | Deliverables |
|---|---|---|
| P2-M5.1 | Remove mock data fallback from API client | Frontend Engineer | api.ts calls real endpoints only |
| P2-M5.2 | Add Vite proxy for HA Ingress | Frontend Engineer | HA Ingress-compatible base URL |
| P2-M5.3 | Add loading/error states to all pages | Frontend Engineer | Skeleton loaders, error boundaries |
| P2-M5.4 | End-to-end testing with running backend | QA Engineer | Full user flow verification |

### P2-M6: Integration & Release
**Complexity:** Low | **Dependencies:** All above

| Task | Agent | Deliverables |
|---|---|---|
| P2-M6.1 | End-to-end HA deployment test | QA Engineer | Install add-on, create profile, log entries |
| P2-M6.2 | Performance benchmarking | QA Engineer | Analysis pipeline timing, DB query performance |
| P2-M6.3 | Security review | Security Engineer | Dependency audit, threat model review |
| P2-M6.4 | Documentation update | Doc Engineer | User guide, upgrade notes, HA add-on docs |
| P2-M6.5 | Graphify update | Knowledge Engineer | Index all Phase 2 nodes |
| P2-M6.6 | Architecture review | Architect | Verify HA isolation, ADR compliance |

---

## 3. Execution Order

```
P2-M1 (HA Bridge) ──────────────────────────────────────┐
     │                                                    │
     ├──► P2-M2 (HA Packaging) ─────────────────────┐    │
     │                                               │    │
     ├──► P2-M4 (Encryption) ───────────────────────┤    │
     │                                               ├──► P2-M6 (Release)
     ├──► P2-M3 (Legacy Migration) ──────────────────┤    │
     │                                               │    │
     └──► P2-M5 (Frontend Integration) ──────────────┘    │

P2-M1, P2-M3, P2-M4 are parallel (no interdependencies).
P2-M2 depends on P2-M1 (needs HA Bridge package).
P2-M5 depends on P2-M1 + P2-M2.
P2-M6 is the final gate.
```

---

## 4. Immediate Next Action

**P2-M1: Build HA Bridge Service** — the critical path item. All other Phase 2 milestones depend on or benefit from it.
