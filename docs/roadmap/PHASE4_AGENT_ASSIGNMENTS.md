# Phase 4 Agent Assignment Plan

> **Date:** 2026-07-26 | **Principle:** Maximize parallel execution  
> **Engineers available:** 5 | **Parallel tracks:** 3

---

## Agent Roster

| Agent | Abbreviation | Primary Skills |
|---|---|---|
| **Architect** | ARCH | ADRs, Graphify, oversight, planning |
| **Backend Engineer** | BE | Python, FastAPI, engines, REST, WebSocket |
| **Frontend Engineer** | FE | React, TypeScript, Vite, WebSocket client |
| **Database Engineer** | DB | SQLAlchemy, Alembic, migrations, models |
| **HA Engineer** | HAE | HA Bridge, entities, Lovelace, config |
| **QA Engineer** | QA | pytest, Playwright, integration testing |
| **Release Engineer** | REL | Release gates, VS validation, Docker |
| **Graphify Engineer** | GRAPH | Graphify nodes, edges, index |
| **Documentation Engineer** | DOCS | README, guides, branding assets |
| **DevOps Engineer** | DEVOPS | CI/CD, Docker, multi-arch builds |
| **Security Engineer** | SEC | Security reviews, dependency scanning |

---

## Prerequisites — Assignment

| ID | Task | Owner | Reason |
|---|---|---|---|
| PREQ-1 | 3A.8 — Frontend WebSocket alignment | **FE** | TypeScript type updates, hook modification |
| PREQ-2 | TD-003 — Multi-arch Docker builds | **DEVOPS** | CI workflow modification, QEMU setup |
| PREQ-3 | TD-010 — C8 dashboard indicator | **FE** | React hook debugging, state propagation |

**All 3 prerequisites can run in parallel.** Zero shared dependencies.

---

## Phase 4A — Assignment Matrix

### Track 1: Schema & ADR (Backend Engineer + Architect)

| ID | Task | Owner |
|---|---|---|
| 4A.1 | Schema consolidation (TD-008) | **BE** |
| 4A.8 | Error response standardization | **BE** |
| 4A.10 | ADR accuracy updates | **ARCH** |

**Execution order:** 4A.1 first (schema changes ripple). Then 4A.8 + 4A.10 in parallel.

### Track 2: Pregnancy Engine (Database + Backend)

| ID | Task | Owner |
|---|---|---|
| 4A.4 | Pregnancy data model | **DB** |
| 4A.5 | Pregnancy engine | **BE** |
| 4A.6 | Pregnancy REST endpoints | **BE** |

**Execution order:** 4A.4 → 4A.5 → 4A.6 (sequential dependency chain).

### Track 3: Frontend & Branding (Frontend + Docs + Backend)

| ID | Task | Owner |
|---|---|---|
| 4A.2 | Branding assets | **DOCS** (+ FE for icon design) |
| 4A.3 | OpenAPI documentation | **BE** |
| 4A.7 | Pregnancy frontend | **FE** |
| 4A.9 | Cycle explanation (AI) | **BE** |

**Execution order:** 4A.2 + 4A.3 + 4A.9 in parallel. 4A.7 after 4A.6 (needs API).

---

## Phase 4B — Assignment Matrix

### Track 1: Data & Backend

| ID | Task | Owner |
|---|---|---|
| 4B.1 | Symptom catalog model | **DB** |
| 4B.2 | Medication model | **DB** |
| 4B.3 | Symptom catalog endpoints | **BE** |
| 4B.4 | Medication endpoints | **BE** |
| 4B.7 | HA entities update | **HAE** |
| 4B.8 | WebSocket heartbeat | **BE** |

### Track 2: Frontend

| ID | Task | Owner |
|---|---|---|
| 4B.5 | Symptom catalog frontend | **FE** |
| 4B.6 | Medication frontend | **FE** |

### Integration

| ID | Task | Owner |
|---|---|---|
| 4B.9 | Phase 4B integration test + Graphify | **QA** + **GRAPH** |

---

## Phase 4C — Assignment Matrix

| ID | Task | Owner |
|---|---|---|
| 4C.1 | Sleep engine | **BE** |
| 4C.2 | Sleep data model | **DB** |
| 4C.3 | Sleep REST | **BE** |
| 4C.4 | Sleep frontend | **FE** |
| 4C.5 | Sleep-Fertility correlation | **BE** |

---

## Phase 4D — Assignment Matrix

| ID | Task | Owner |
|---|---|---|
| 4D.1 | Nutrition engine | **BE** |
| 4D.2 | Nutrition data model | **DB** |
| 4D.3 | Nutrition REST | **BE** |
| 4D.4 | Nutrition frontend | **FE** |

---

## Parallel Execution Map

```
Week 1-2: Phase 4A
═══════════════════════════════════════════════════════════════
Track 1 (BE+ARCH):  4A.1 ──> 4A.8 ──> 4A.10
Track 2 (DB+BE):    4A.4 ──> 4A.5 ──> 4A.6
Track 3 (FE+DOCS):  4A.2 ─────────────> 4A.7
                    4A.3 ──┘
                    4A.9 ─────────────┘
PREQ (FE+DEVOPS):   PREQ-1 ║ PREQ-2 ║ PREQ-3  (all parallel)
                    4A.11 (QA+GRAPH — after all above)
═══════════════════════════════════════════════════════════════

Week 3-4: Phase 4B
═══════════════════════════════════════════════════════════════
Track 1 (DB+BE+HAE): 4B.1 ──> 4B.3 ──> 4B.7
                     4B.2 ──> 4B.4 ──┘
Track 2 (FE):        4B.5
                     4B.6
                     4B.8 (BE)
                     4B.9 (QA+GRAPH — after all above)
═══════════════════════════════════════════════════════════════

Week 5-6: Phase 4C
═══════════════════════════════════════════════════════════════
Track 1 (DB+BE):    4C.2 ──> 4C.1 ──> 4C.3 ──> 4C.5
Track 2 (FE):       4C.4 (after 4C.3)
═══════════════════════════════════════════════════════════════

Week 7-8: Phase 4D
═══════════════════════════════════════════════════════════════
Track 1 (DB+BE):    4D.2 ──> 4D.1 ──> 4D.3
Track 2 (FE):       4D.4 (after 4D.3)
═══════════════════════════════════════════════════════════════
```

---

## Engineer Workload Summary

| Engineer | Prerequisites | 4A | 4B | 4C | 4D | Total Tasks |
|---|---|---|---|---|---|---|
| **Backend Engineer** | — | 4 tasks | 3 tasks | 3 tasks | 2 tasks | **12** |
| **Frontend Engineer** | 2 tasks | 1 task | 2 tasks | 1 task | 1 task | **7** |
| **Database Engineer** | — | 1 task | 2 tasks | 1 task | 1 task | **5** |
| **DevOps Engineer** | 1 task | — | — | — | — | **1** |
| **HA Engineer** | — | — | 1 task | — | — | **1** |
| **QA Engineer** | — | 1 task | 1 task | — | — | **2** |
| **Architect** | — | 1 task | — | — | — | **1** |
| **Documentation** | — | 1 task | — | — | — | **1** |
| **Graphify** | — | 1 task | 1 task | — | — | **2** |

**Backend Engineer is the busiest.** Frontend and Database have significant idle time after their track is done — they can assist with QA, Graphify, or documentation during those periods.

---

## Dispatch Rules

1. **Never assign 2 tasks to the same engineer simultaneously** — each engineer works one task at a time.
2. **Tasks marked as parallel** in the WBS can be dispatched simultaneously to different engineers.
3. **After every task completion**, run `python -m pytest packages/ -q`. If tests fail, stop and remediate before dispatching the next task.
4. **After every frontend task**, run `npm run build` from `frontend/`.
5. **Commits must be grouped by work package** — one commit per completed task.
6. **Graphify updates happen at integration milestones** (4A.11, 4B.9), not after every task.
