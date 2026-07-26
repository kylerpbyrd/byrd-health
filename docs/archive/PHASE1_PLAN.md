# Phase 1 Implementation Plan — Platform Foundation

> Status: Ready for execution | Date: 2026-07-23

---

## 1. Phase 1 Overview

**Objective:** Create the core Byrd Health architecture as a set of independent, testable, portable services. No Home Assistant code. No production deployment. Pure platform.

**Exit Criteria:**
- All four Phase 1 services are scaffolded and passing tests
- Database migrations are defined and validated
- API endpoints are documented and functional
- Frontend renders with mock data
- CI pipeline runs tests, linting, and type checking
- Graphify is updated with all service relationships

---

## 2. Milestones

### M1: Repository & Tooling Setup
**Complexity:** Low | **Dependencies:** None

| Task | Agent | Deliverables |
|---|---|---|
| M1.1 | Initialize monorepo structure | DevOps Engineer | Directory layout, `.gitignore`, root configs |
| M1.2 | Set up Python project config | Backend Engineer | `pyproject.toml`, `uv.lock`, venv setup |
| M1.3 | Set up CI pipeline | DevOps Engineer | `.github/workflows/ci.yml` — test, lint, mypy |
| M1.4 | Set up pre-commit hooks | DevOps Engineer | lint, format, type-check on commit |

**Acceptance:** `pytest`, `mypy`, and `ruff` pass on a clean checkout.

---

### M2: Fertility Engine Package
**Complexity:** Medium | **Dependencies:** M1

| Task | Agent | Deliverables |
|---|---|---|
| M2.1 | Extract `coverline.py` to typed module | AI Engineer | `fertility_engine/coverline.py` with Pydantic I/O |
| M2.2 | Extract `ovulation.py` to typed module | AI Engineer | `fertility_engine/ovulation.py` with Pydantic I/O |
| M2.3 | Extract `fertile_window.py` to typed module | AI Engineer | `fertility_engine/fertile_window.py` with Pydantic I/O |
| M2.4 | Extract `cycle_analysis.py` orchestrator | AI Engineer | `fertility_engine/analysis.py` — pure function |
| M2.5 | Create Pydantic models for all I/O types | AI Engineer | `fertility_engine/models.py` — TemperatureRecord, CycleInsights, etc. |
| M2.6 | Write algorithm unit tests (from legacy + new) | QA Engineer | `tests/unit/test_coverline.py`, `test_ovulation.py`, `test_fertile_window.py`, `test_analysis.py` |
| M2.7 | Write property-based tests | QA Engineer | Hypothesis tests for algorithm invariants |

**Acceptance:**
- All algorithm tests pass with 95%+ coverage
- Same inputs produce same outputs as legacy algorithms (regression test)
- Package is pip-installable: `pip install -e packages/fertility_engine`

**Expected files:**
```
packages/fertility_engine/
├── pyproject.toml
├── src/fertility_engine/
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── coverline.py       # Ported from legacy
│   ├── ovulation.py       # Ported from legacy
│   ├── fertile_window.py  # Ported from legacy
│   ├── analysis.py        # Orchestrator (ported + split)
│   └── prediction.py      # Period prediction (ported)
└── tests/
    ├── test_coverline.py
    ├── test_ovulation.py
    ├── test_fertile_window.py
    ├── test_analysis.py
    └── test_regression.py  # Legacy compatibility
```

---

### M3: Data Service Package
**Complexity:** Medium | **Dependencies:** M1

| Task | Agent | Deliverables |
|---|---|---|
| M3.1 | Define SQLAlchemy models | Database Engineer | `data_service/models.py` — Profile, Cycle, Temperature, FertilitySigns, Symptom, ComputedInsights |
| M3.2 | Define Pydantic schemas | Backend Engineer | `data_service/schemas.py` — Create/Read/Update schemas |
| M3.3 | Create initial Alembic migration | Database Engineer | `data_service/migrations/versions/001_initial.py` |
| M3.4 | Implement repository classes | Database Engineer | `data_service/repositories.py` — ProfileRepo, CycleRepo, etc. |
| M3.5 | Implement DataService facade | Database Engineer | `data_service/service.py` — unified interface |
| M3.6 | Write data layer tests | QA Engineer | `tests/unit/test_models.py`, `test_repositories.py`, `test_migrations.py` |

**Acceptance:**
- All data tests pass with 85%+ coverage
- Alembic upgrade/downgrade works on SQLite
- Repositories enforce profile-level data isolation
- Package is pip-installable: `pip install -e packages/data_service`

**Expected files:**
```
packages/data_service/
├── pyproject.toml
├── src/data_service/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── repositories.py    # CRUD operations
│   ├── service.py         # DataService facade
│   ├── database.py        # Engine + session factory
│   └── migrations/
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
│           └── 001_initial_schema.py
└── tests/
    ├── conftest.py         # Test fixtures (in-memory SQLite)
    ├── test_models.py
    ├── test_repositories.py
    └── test_migrations.py
```

---

### M4: Web API Service
**Complexity:** Medium | **Dependencies:** M2, M3

| Task | Agent | Deliverables |
|---|---|---|
| M4.1 | Create FastAPI app scaffold | Backend Engineer | `web_api/app.py` with router structure |
| M4.2 | Implement profile endpoints | Backend Engineer | `web_api/routers/profiles.py` |
| M4.3 | Implement entry endpoints | Backend Engineer | `web_api/routers/entries.py` |
| M4.4 | Implement cycle endpoints | Backend Engineer | `web_api/routers/cycles.py` |
| M4.5 | Implement insights endpoints | Backend Engineer | `web_api/routers/insights.py` |
| M4.6 | Implement export endpoint | Backend Engineer | `web_api/routers/export.py` |
| M4.7 | Set up dependency injection | Backend Engineer | `web_api/dependencies.py` |
| M4.8 | Write API integration tests | QA Engineer | `tests/integration/test_api_*.py` |

**Acceptance:**
- All API tests pass with 80%+ coverage
- OpenAPI docs render at `/docs`
- All endpoints validated with Pydantic schemas
- API is versioned: `/api/v1/fertility/...`
- Health check endpoint responds: `GET /api/health`

**Expected files:**
```
packages/web_api/
├── pyproject.toml
├── src/web_api/
│   ├── __init__.py
│   ├── app.py              # FastAPI app, lifespan
│   ├── config.py           # Settings from env vars
│   ├── dependencies.py     # Depends() functions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── profiles.py
│   │   ├── entries.py
│   │   ├── cycles.py
│   │   ├── insights.py
│   │   └── export.py
│   └── schemas/
│       ├── __init__.py
│       ├── entries.py
│       ├── cycles.py
│       └── profiles.py
└── tests/
    ├── conftest.py
    ├── test_api_profiles.py
    ├── test_api_entries.py
    ├── test_api_cycles.py
    └── test_api_insights.py
```

---

### M5: Web Frontend Scaffold
**Complexity:** Medium | **Dependencies:** M1

| Task | Agent | Deliverables |
|---|---|---|
| M5.1 | Initialize Vite + React + TypeScript | Frontend Engineer | Project scaffold with Tailwind + shadcn/ui |
| M5.2 | Set up routing and layout | Frontend Engineer | `App.tsx` with React Router, `Layout.tsx` |
| M5.3 | Create API client | Frontend Engineer | `lib/api.ts` with fetch wrapper |
| M5.4 | Create TanStack Query setup | Frontend Engineer | `lib/query-client.ts` |
| M5.5 | Create type definitions | Frontend Engineer | `types/fertility.ts` matching Pydantic schemas |
| M5.6 | Scaffold Dashboard page (mock data) | Frontend Engineer | `pages/DashboardPage.tsx` |
| M5.7 | Scaffold Entry page (mock data) | Frontend Engineer | `pages/EntryPage.tsx` |
| M5.8 | Scaffold History page (mock data) | Frontend Engineer | `pages/HistoryPage.tsx` |
| M5.9 | Create shared components | Frontend Engineer | `PhaseBanner`, `StatTile`, `BBTChart` (Recharts) |
| M5.10 | Write component tests | QA Engineer | Vitest + React Testing Library |

**Acceptance:**
- Frontend builds successfully: `npm run build`
- All pages render with mock data
- Component tests pass with 70%+ coverage
- Responsive layout (mobile + desktop)
- Lighthouse accessibility score ≥ 90

**Expected files:**
```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── index.html
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── EntryPage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── CycleDetailPage.tsx
│   │   ├── ProfilesPage.tsx
│   │   └── SettingsPage.tsx
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── PhaseBanner.tsx
│   │   ├── StatTile.tsx
│   │   ├── BBTChart.tsx
│   │   └── EntryForm.tsx
│   ├── hooks/
│   │   ├── useProfile.ts
│   │   └── useCycle.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── query-client.ts
│   │   └── utils.ts
│   └── types/
│       └── fertility.ts
└── tests/
    ├── setup.ts
    ├── DashboardPage.test.tsx
    ├── EntryForm.test.tsx
    └── PhaseBanner.test.tsx
```

---

### M6: Integration & Polish
**Complexity:** Low | **Dependencies:** M4, M5

| Task | Agent | Deliverables |
|---|---|---|
| M6.1 | Wire frontend to real API | Frontend Engineer | Replace mock data with API calls |
| M6.2 | End-to-end smoke test | QA Engineer | Create profile → log entry → view dashboard |
| M6.3 | Documentation | Documentation Engineer | Developer setup guide, API docs, architecture overview |
| M6.4 | Graphify update | Knowledge Engineer | Index all Phase 1 entities, services, relationships |
| M6.5 | Architecture review | Architect | Verify ADR compliance, service boundaries |

**Acceptance:**
- Full flow works: profile creation → entry logging → dashboard display → chart rendering
- All CI checks pass (test + lint + typecheck)
- Developer can clone → install → run → see dashboard
- Graphify contains all Phase 1 nodes and edges

---

## 3. Repository Structure (post-Phase-1)

```
byrd-health/
├── packages/
│   ├── fertility_engine/       # Pure algorithm package
│   ├── data_service/           # Database + migrations
│   └── web_api/                # FastAPI REST + WebSocket
├── frontend/                   # React SPA (Vite)
├── tools/
│   └── legacy-migrate/         # Legacy data migration (Phase 2)
├── docs/
│   ├── adr/                    # 10 ADRs
│   ├── LEGACY_REVIEW.md
│   ├── MIGRATION_PLAN.md
│   ├── ARCHITECTURE_RECOMMENDATIONS.md
│   ├── GRAPHIFY_INDEX_PLAN.md
│   └── PHASE1_PLAN.md
├── graph/                      # Graphify knowledge graph
│   ├── index.json
│   ├── edges.json
│   └── nodes/
├── .github/workflows/          # CI pipeline
├── AGENTS.md
├── PROJECTPLAN.md
└── README.md
```

---

## 4. Agent Assignments Summary

| Agent | Milestones | Primary Deliverables |
|---|---|---|
| Backend Engineer | M1, M4 | Web API, project config |
| AI/Data Science Engineer | M2 | Fertility Engine |
| Database Engineer | M3 | Data Service, schema |
| Frontend Engineer | M5 | React SPA, Recharts |
| QA Engineer | M2, M3, M4, M5, M6 | All tests |
| DevOps Engineer | M1 | CI, tooling |
| Documentation Engineer | M6 | Developer docs |
| Knowledge Engineer | M6 | Graphify indexing |
| Architect | All | Review, approval |

---

## 5. Execution Order

```
M1 (Tooling) ─────────────────────────────────────────────┐
     │                                                      │
     ├──► M2 (Fertility Engine) ──┐                        │
     │                            ├──► M4 (Web API) ──┐    │
     ├──► M3 (Data Service) ──────┘                   ├──► M6 (Integration)
     │                                                 │
     └──► M5 (Frontend) ──────────────────────────────┘

M2 and M3 are parallel — they have no interdependencies.
M4 depends on M2 + M3 (needs both packages).
M5 runs in parallel with M2/M3/M4 (starts with mock data, integrates later).
M6 is the final integration gate.
```

---

## 6. Phase 1 Binary Start

To begin Phase 1, delegate M1 to DevOps Engineer:

> **Agent:** DevOps Engineer
> **Objective:** Initialize the Byrd Health monorepo structure with Python tooling and CI pipeline.
> **References:** ADR-0001, ADR-0003, ADR-0009
> **Deliverables:** `pyproject.toml`, CI config, directory structure, pre-commit hooks

M2 and M3 can begin once M1 is complete.
