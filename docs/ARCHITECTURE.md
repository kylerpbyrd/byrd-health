# Platform Architecture — Byrd Health

> Based on [ADR-0001](adr/ADR-0001-platform-architecture.md) and [Architecture Recommendations](ARCHITECTURE_RECOMMENDATIONS.md).

---

## Service Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        Byrd Health Platform                       │
│                                                                   │
│  ┌──────────────┐                            ┌──────────────┐    │
│  │ Web Frontend │                            │  HA Bridge   │    │
│  │ (React SPA)  │                            │ (Phase 2+)   │    │
│  └──────┬───────┘                            └──────┬───────┘    │
│         │                                           │            │
│         ▼                                           ▼            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     API Gateway                              │ │
│  │              (FastAPI — REST + WebSocket)                    │ │
│  └──────────┬──────────────────────────────────────┬───────────┘ │
│             │                                      │              │
│             ▼                                      ▼              │
│  ┌──────────────────────┐           ┌──────────────────────────┐ │
│  │   Fertility Engine   │           │     Data Service          │ │
│  │   (Pure Python)      │◄─────────►│  (SQLAlchemy + Alembic)   │ │
│  └──────────────────────┘           └──────────┬───────────────┘ │
│                                                │                  │
│                                                ▼                  │
│                                      ┌──────────────────────┐    │
│                                      │  SQLite / PostgreSQL  │    │
│                                      └──────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Services

### Web Frontend (`frontend/`)

User-facing SPA for data entry, chart visualization, and cycle tracking.

- **Technology:** React 18+ with TypeScript, Vite, Tailwind CSS, Recharts
- **State:** TanStack Query for server-state caching
- **Testing:** Vitest + React Testing Library
- **Key files:** `src/App.tsx`, `src/pages/`, `src/components/`, `src/lib/api.ts`

### Web API (`packages/web_api/`)

REST + WebSocket gateway that routes requests, validates input, and orchestrates analysis.

- **Technology:** FastAPI + Pydantic v2, Uvicorn
- **Endpoints:** `/api/v1/fertility/profiles`, `/entries`, `/cycles`, `/insights`, `/export`
- **WebSocket:** `/api/v1/fertility/ws` for real-time updates
- **Auth:** Profile-scoped dependency injection (no user auth in Phase 1)
- **Key files:** `src/web_api/app.py`, `src/web_api/routers/`, `src/web_api/dependencies.py`

### Fertility Engine (`packages/fertility_engine/`)

Pure Python algorithms implementing the sympto-thermal method for fertility tracking.

- **Technology:** Pure Python, Pydantic v2 for I/O types
- **Modules:** `coverline.py`, `ovulation.py`, `fertile_window.py`, `analysis.py`, `prediction.py`
- **No dependencies** on FastAPI, databases, or Home Assistant
- **Key files:** All source in `src/fertility_engine/`

### Data Service (`packages/data_service/`)

Database access layer providing CRUD operations and schema management.

- **Technology:** SQLAlchemy 2.0 (async), Alembic migrations
- **Engines:** SQLite (dev/HA) and PostgreSQL (future ByrdOS)
- **Models:** Profile, Cycle, TemperatureRecord, FertilitySigns, Symptom, ComputedInsights
- **Key files:** `src/data_service/models.py`, `src/data_service/repositories.py`, `src/data_service/service.py`

### Future Services (Phase 2-3)

- **HA Bridge** — Publishes entities to Home Assistant, polls sensors, registers Lovelace card
- **Device Adapters** — Bluetooth thermometers, ESPHome, wearable integrations

---

## Data Flow

```
User Entry (Frontend)
       │
       ▼
POST /api/v1/fertility/entries ──────► Web API validates (Pydantic)
       │
       ▼
Data Service persists ──────► SQLite/PostgreSQL
       │
       ▼
Fertility Engine analyzes ──► reads temperatures + signs
       │
       ▼
ComputedInsights stored ───► Data Service persists
       │
       ▼
GET /api/v1/fertility/insights ──────► Frontend displays charts + dashboard
```

All processing is local. No health data leaves the device.

---

## Phase Roadmap

| Phase | Name | Scope |
|---|---|---|
| **0** | Discovery & Architecture | Legacy analysis, migration plan, ADRs (complete) |
| **1** | Platform Foundation | Fertility Engine, Data Service, Web API, Frontend (in progress) |
| **2** | Fertility Service | HA Bridge, encryption at rest, legacy migration |
| **3** | Device Integration | Bluetooth thermometers, ESPHome, wearable adapters |
| **4** | Platform Expansion | Sleep, nutrition, medication modules; ByrdOS integration |

---

## Key Architectural Decisions

All major decisions are formalized as ADRs in [`docs/adr/`](adr/):

| ADR | Decision |
|---|---|
| [ADR-0001](adr/ADR-0001-platform-architecture.md) | Service-oriented architecture with 4 Phase 1 packages |
| [ADR-0002](adr/ADR-0002-frontend-architecture.md) | React + TypeScript + Vite for web frontend |
| [ADR-0003](adr/ADR-0003-database-strategy.md) | SQLAlchemy 2.0 + Alembic with SQLite/PostgreSQL portability |
| [ADR-0004](adr/ADR-0004-user-profile-model.md) | Multi-profile architecture with UUID primary keys |
| [ADR-0005](adr/ADR-0005-legacy-migration-strategy.md) | Reference-only legacy code, rewrite from scratch |
| [ADR-0006](adr/ADR-0006-home-assistant-integration-boundary.md) | HA Bridge isolated — all other services HA-free |
| [ADR-0007](adr/ADR-0007-ai-prediction-architecture.md) | Pure Python algorithms with Pydantic I/O |
| [ADR-0008](adr/ADR-0008-security-and-privacy-model.md) | Encryption at rest deferred to Phase 2 |
| [ADR-0009](adr/ADR-0009-testing-strategy.md) | pytest, Vitest, mypy strict, CI pipeline |
| [ADR-0010](adr/ADR-0010-graphify-knowledge-architecture.md) | Graphify canonical knowledge graph |

---

## Design Principles

1. **Privacy-first** — All processing local, no external data transmission, encryption-ready
2. **Modularity** — Replaceable services, clear boundaries, no vendor lock-in
3. **Portability** — Business logic independent of deployment (HA Add-on vs. ByrdOS)
4. **Isolation** — HA Bridge is the ONLY service aware of Home Assistant
5. **Explainability** — Every insight traceable to underlying data and rules
