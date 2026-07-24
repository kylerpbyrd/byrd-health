# ADR-0001: Platform Architecture

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None (initial architecture)                    |
| **Scope**    | Entire Byrd Health platform                    |

---

## 1. Context

Byrd Health is a privacy-first, self-hosted health intelligence platform. The first service is fertility intelligence.

Constraints:
- Must deploy as a Home Assistant Add-on initially (Phase 2-3)
- Must remain architecturally prepared for ByrdOS integration (future)
- Must not create ByrdOS dependencies during development
- Must follow privacy-first, local-first principles
- Must support modular expansion (sleep, nutrition, medication, etc.)

## 2. Decision

Adopt a **service-oriented architecture** with six services and strict isolation of deployment-specific integration code.

### 2.1 Service Boundaries

```
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Web Frontend │  │  HA Bridge   │  │ Device Adapters   │
│ (React SPA)  │  │ (isolated)   │  │ (pluggable)       │
└──────┬───────┘  └──────┬───────┘  └────────┬──────────┘
       │                 │                    │
       ▼                 ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                  │
│                 REST + WebSocket + Auth                   │
└──────────┬───────────────────────────────┬───────────────┘
           │                               │
           ▼                               ▼
┌─────────────────────┐        ┌───────────────────────────┐
│  Fertility Engine   │        │      Data Service          │
│  (pure Python pkg)  │◄──────►│  (SQLAlchemy + Alembic)    │
└─────────────────────┘        └─────────────┬─────────────┘
                                             │
                                             ▼
                                   ┌─────────────────────┐
                                   │  SQLite / PostgreSQL │
                                   └─────────────────────┘
```

### 2.2 Technology Choices

| Component          | Technology               | Rationale                                       |
|--------------------|--------------------------|-------------------------------------------------|
| Web framework      | FastAPI                  | Async-native, OpenAPI, Pydantic integration     |
| ASGI server        | Uvicorn                  | Production-grade, lightweight                   |
| ORM                | SQLAlchemy 2.0           | Async, engine-agnostic (SQLite ↔ PostgreSQL)    |
| Migrations         | Alembic                  | Standard for SQLAlchemy                         |
| Validation         | Pydantic v2              | Type-safe, FastAPI-native                       |
| Frontend framework | React + TypeScript       | Component model, ecosystem, ByrdOS portable     |
| Frontend build     | Vite                     | Fast, modern dev experience                     |
| Styling            | Tailwind CSS + shadcn/ui | Utility-first, design system                    |
| Charting           | Recharts                 | React-native, TypeScript-friendly               |
| HA Card            | Lit + TypeScript         | Web component standard for HA (Phase 3)         |
| HTTP client        | httpx (async)            | For HA Bridge REST calls                        |
| Background tasks   | asyncio / BackgroundTasks | Lightweight for single-user; queue later        |
| Testing            | pytest + pytest-asyncio   | Industry standard                               |
| Type checking      | mypy (strict)            | Code quality                                    |

### 2.3 Isolation Principle

**The HA Bridge is the ONLY service allowed to import or reference Home Assistant APIs.** All other services are pure Python with zero HA dependencies.

## 3. Consequences

### Positive
- Clear boundaries enable independent development and testing
- Fertility Engine is directly portable to any deployment target
- Future health modules (sleep, nutrition) follow the same pattern
- ByrdOS integration requires only replacing HA Bridge with ByrdOS Bridge

### Negative
- More services to orchestrate vs. a monolith
- Inter-service communication overhead (mitigated: in-process for HA add-on)
- More complex initial setup

### Risks
- Service boundary violations (mitigated by mypy strict + import linting)
- Over-engineering for single-user HA add-on (mitigated: deploy as single container)

## 4. Phase 1 Scope

Phase 1 implements the **platform foundation without HA-specific code**:
1. `fertility_engine` — pure algorithm package
2. `data_service` — SQLAlchemy models + Alembic migrations
3. `web_api` — FastAPI routes + Pydantic schemas
4. `web_frontend` — React scaffold + Tailwind + Recharts

HA Bridge and Device Adapters begin in Phase 2-3.

## 5. References

- `docs/LEGACY_REVIEW.md` — Analysis of existing application
- `docs/ARCHITECTURE_RECOMMENDATIONS.md` — Detailed architecture recommendations
- `PROJECTPLAN.md` — Project phases
