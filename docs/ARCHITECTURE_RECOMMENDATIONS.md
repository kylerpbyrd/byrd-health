# Architecture Recommendations — Byrd Health

> Target: Privacy-first, modular health platform deployable as HA Add-on with future ByrdOS compatibility.

---

## 1. Guiding Principles

All architectural decisions are governed by:

1. **Privacy-first** — Local processing, no external data transmission, encryption at rest
2. **Modularity** — Replaceable services, clear boundaries, independent testability
3. **Portability** — Business logic independent of deployment environment (HA Add-on vs. ByrdOS)
4. **Explainability** — Every insight must be traceable to underlying data and rules
5. **Future-proofing** — Stable APIs, documented integration points, no vendor lock-in

---

## 2. Service Boundaries

```
┌──────────────────────────────────────────────────────────────────┐
│                        Byrd Health Platform                       │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Web Frontend │  │  HASS Bridge │  │  Device Integrations   │ │
│  │  (React SPA)  │  │  (HA Add-on) │  │  (BT, ESPHome, etc.)  │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                 │                       │              │
│         ▼                 ▼                       ▼              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     API Gateway                              │ │
│  │              (FastAPI — REST + WebSocket)                    │ │
│  └──────────┬──────────────────────────────────────┬───────────┘ │
│             │                                      │              │
│             ▼                                      ▼              │
│  ┌──────────────────────┐           ┌──────────────────────────┐ │
│  │   Fertility Engine   │           │     Data Service          │ │
│  │   (Algorithm lib)    │◄─────────►│  (SQLAlchemy + Alembic)   │ │
│  └──────────────────────┘           └──────────┬───────────────┘ │
│                                                │                  │
│                                                ▼                  │
│                                      ┌──────────────────────┐    │
│                                      │    SQLite / PG       │    │
│                                      │    (encrypted)       │    │
│                                      └──────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 2.1 Service Descriptions

| Service | Responsibility | Technology | HA Dependency |
|---|---|---|---|
| **Web Frontend** | User interface, charts, data entry | React + TypeScript + Chart.js | None |
| **API Gateway** | REST endpoints, WebSocket, auth, request routing | FastAPI + Pydantic | None |
| **Fertility Engine** | Algorithmic analysis: ovulation, fertile window, predictions | Pure Python package | None |
| **Data Service** | CRUD operations, schema management, encryption | SQLAlchemy 2.0 + Alembic | None |
| **HA Bridge** | HA entity publishing, sensor polling, Lovelace card | httpx (async) + WebSocket | Yes (isolated) |
| **Device Integrations** | Bluetooth thermometers, ESPHome, wearables | Adapter pattern | No (direct) |

---

## 3. Backend Architecture

### 3.1 Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| Web framework | **FastAPI** | Async-native, automatic OpenAPI docs, Pydantic integration, high performance |
| ASGI server | **Uvicorn** + Gunicorn | Production-grade, multi-worker support |
| ORM | **SQLAlchemy 2.0** | Async support, mature, engine-agnostic |
| Migrations | **Alembic** | De facto standard for SQLAlchemy |
| Validation | **Pydantic v2** | FastAPI-native, Rust-core for performance |
| Background tasks | **asyncio** (single-user) / **Celery** or **ARQ** (multi-user) | Lightweight for HA, scalable for ByrdOS |
| HTTP client | **httpx** (async) | Modern, async, connection pooling |
| WebSocket | **FastAPI WebSocket** | Built-in, same framework |
| Testing | **pytest** + **pytest-asyncio** + **httpx.AsyncClient** | Industry standard |
| Type checking | **mypy** (strict mode) | Essential for large Python codebases |

### 3.2 API Design

**Base URL pattern:**
```
/api/v1/fertility/{resource}
```

**Core endpoints (mapped from legacy):**

| Legacy Route | New Endpoint | Method | Description |
|---|---|---|---|
| `GET /` | `GET /api/v1/fertility/dashboard` | GET | Dashboard insights |
| `GET/POST /entry` | `POST /api/v1/fertility/entries` | POST | Log daily entry |
| `GET /history` | `GET /api/v1/fertility/cycles` | GET | List cycles |
| `GET /history/<id>` | `GET /api/v1/fertility/cycles/{id}` | GET | Cycle detail |
| `GET /api/chart-data/<id>` | `GET /api/v1/fertility/cycles/{id}/chart` | GET | Chart data |
| `POST /api/entry` | `POST /api/v1/fertility/entries` | POST | JSON entry (HA automation) |
| `GET /api/insights` | `GET /api/v1/fertility/insights` | GET | Current insights |
| `GET/POST /profiles` | `GET/POST /api/v1/fertility/profiles` | GET/POST | Profile management |
| `GET/POST /settings` | `GET/PATCH /api/v1/fertility/profiles/{id}/settings` | GET/PATCH | Profile settings |
| `POST /new-cycle` | `POST /api/v1/fertility/cycles` | POST | Start new cycle |
| `GET /export` | `GET /api/v1/fertility/profiles/{id}/export` | GET | Data export |

**WebSocket endpoint:**
```
WS /api/v1/fertility/ws
```
Provides real-time updates for dashboard, chart data changes, and HA entity state changes.

**API versioning:** All endpoints under `/api/v{n}/`. Backward compatibility maintained for at least one prior version.

### 3.3 Dependency Injection Pattern

```python
# FastAPI dependency injection — replaces Flask g object
async def get_data_service() -> DataService: ...
async def get_fertility_engine() -> FertilityEngine: ...
async def get_ha_bridge() -> Optional[HABridge]: ...

@router.get("/api/v1/fertility/dashboard")
async def dashboard(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
    engine: FertilityEngine = Depends(get_fertility_engine),
) -> DashboardResponse: ...
```

---

## 4. Frontend Architecture

### 4.1 Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| Framework | **React 18+** with TypeScript | Component model, ecosystem, HA card compatibility |
| Build tool | **Vite** | Fast, modern, good HMR |
| State management | **TanStack Query** (React Query) | Server-state caching, auto-refetch, optimistic updates |
| Charting | **Chart.js 4.x** with react-chartjs-2 | Familiar from legacy, annotation plugin, good performance |
| Styling | **Tailwind CSS** | Utility-first, tree-shakeable, design-system compatible |
| Testing | **Vitest** + **React Testing Library** | Vite-native, fast |
| PWA | **Workbox** (via Vite PWA plugin) | Offline support, service worker |
| Accessibility | **Radix UI** primitives | WCAG-compliant, unstyled, composable |

### 4.2 Component Architecture

```
src/
├── pages/
│   ├── Dashboard/
│   ├── Entry/
│   ├── History/
│   ├── CycleDetail/
│   ├── Profiles/
│   └── Settings/
├── components/
│   ├── BBTChart/           # Chart.js wrapper
│   ├── PhaseBanner/        # Cycle phase indicator
│   ├── StatTile/           # Reusable stat display
│   ├── EntryForm/          # Daily log form
│   ├── SymptomSelector/    # Symptom checkboxes
│   ├── FertilitySignsGrid/ # Signs radio groups
│   ├── CycleTable/         # History table
│   ├── ProfileCard/        # Profile management card
│   └── WarningsList/       # Alerts/warnings display
├── hooks/
│   ├── useCycleData.ts     # TanStack Query hooks
│   ├── useProfileData.ts
│   └── useWebSocket.ts     # Real-time updates
├── services/
│   └── api.ts              # API client (fetch wrapper)
├── types/
│   └── fertility.ts        # TypeScript interfaces
└── utils/
    └── formatters.ts       # Date, temp, phase formatters
```

### 4.3 HA Lovelace Card

The Lovelace card remains a **standalone Lit web component** (not React-based) for HA ecosystem compatibility:

- **Technology:** Lit 3.x + TypeScript
- **Deployment:** Served from `/local/bbt-card.js` via HA's www directory
- **Data source:** Reads from published HA entity states (no API dependency)
- **Configuration:** Standard HA card YAML config
- **Updates:** Subscribes to HA state changes via `hass` object

---

## 5. Database Strategy

### 5.1 Schema Design

The legacy schema is fundamentally sound. Recommended enhancements:

**Tables to KEEP (with modernized types):**
- `profiles` → Add `id` (UUID), `encryption_key_hash`, `created_at`, `updated_at`
- `cycles` → Add `id` (UUID), `is_archived`
- `temperatures` → Add proper `TIMESTAMP` for `time_taken`, indexing on `(cycle_id, date)`
- `fertility_signs` → Same structure, add indexing
- `symptoms` → Same structure
- `computed_insights` → Add `engine_version` for algorithm version tracking

**Tables to ADD:**
- `audit_log` → Track access and modifications
- `data_encryption_keys` → Per-profile encryption key management
- `device_readings` → Raw device data separate from validated/logged data
- `health_modules` → Registry for future health modules (sleep, nutrition, etc.)

### 5.2 Engine Strategy

| Deployment | Database | Rationale |
|---|---|---|
| HA Add-on | SQLite (WAL) | Zero-config, filesystem-local, sufficient for single-user |
| ByrdOS (single-user) | SQLite (WAL) | Same benefits |
| ByrdOS (multi-user) | PostgreSQL 16+ | Concurrent writes, connection pooling, proper auth |

Both engines supported via SQLAlchemy — single codebase, config-driven engine selection.

### 5.3 Encryption at Rest

Health data must be encrypted at rest:

- **Per-profile encryption** using AES-256-GCM
- Encryption key derived from a master key stored in HA secrets or ByrdOS keychain
- SQLite: Application-layer encryption of sensitive columns (temp_value, fertility data)
- PostgreSQL: pgcrypto extension or column-level encryption
- Backup files must also be encrypted

### 5.4 Migration Path

1. Define new schema in SQLAlchemy models
2. Create Alembic migration that reads legacy `bbt.db` schema
3. Map and transform data to new schema
4. Apply encryption to sensitive columns during migration
5. Validate completeness and integrity post-migration

---

## 6. Home Assistant Integration Approach

### 6.1 Architecture Principle

**The HA Bridge is the ONLY component with Home Assistant dependencies.** All other services (Fertility Engine, Data Service, Web Frontend) must have zero HA imports.

```
HA Bridge (isolated)
    │
    │  Only this service knows about:
    │  - Supervisor API (http://supervisor/core/api)
    │  - Entity ID conventions
    │  - Lovelace card format
    │  - bashio configuration
    │
    ▼
All other services ← pure Python, no HA knowledge
```

### 6.2 HA Bridge Responsibilities

1. **Entity Publishing** — POST entity states after analysis completes
2. **Sensor Polling** — GET sensor states on configurable interval
3. **Lovelace Registration** — Register card as HA resource
4. **Config Translation** — Read bashio config → internal settings model
5. **Ingress Support** — Handle X-Ingress-Path header
6. **WebSocket Bridge** — Forward HA state changes to internal WebSocket

### 6.3 Entity Design (preserved from legacy)

Same 9 entities per profile — these are proven and HA users have automations built on them:

```
sensor.bbt_{slug}_cycle_day
sensor.bbt_{slug}_cycle_phase
sensor.bbt_{slug}_last_temp
binary_sensor.bbt_{slug}_fertile_window
binary_sensor.bbt_{slug}_ovulation_confirmed
sensor.bbt_{slug}_ovulation_date
sensor.bbt_{slug}_next_period_date
sensor.bbt_{slug}_luteal_length
sensor.bbt_{slug}_avg_cycle_length
```

### 6.4 Add-on Packaging

- Keep the HA Add-on format — `config.yaml`, `Dockerfile`, `run.sh`
- Add-on is a containerized deployment of all services
- Single process during Phase 2 (FastAPI serves both API and static frontend)
- Future: Frontend can be served by HA Ingress or as standalone PWA
- `config.yaml` exposes: temp_unit, ha_sensor_entity, poll_interval, encryption_enabled

---

## 7. API Strategy

### 7.1 API Design Principles

- **RESTful** for CRUD operations
- **WebSocket** for real-time state updates
- **Versioned** — `/api/v1/`, `/api/v2/`, etc.
- **OpenAPI 3.1** — auto-generated by FastAPI, served at `/docs`
- **JSON** request/response bodies with Pydantic validation
- **Health check** endpoint at `/api/health`
- **Consistent error format:** `{"error": "message", "detail": "...", "code": "ERROR_CODE"}`

### 7.2 Endpoint Grouping

| Prefix | Scope | Auth Required |
|---|---|---|
| `/api/v1/fertility/entries` | Temperature and sign logging | Profile |
| `/api/v1/fertility/cycles` | Cycle management and history | Profile |
| `/api/v1/fertility/profiles` | Profile CRUD | Admin (multi-user) |
| `/api/v1/fertility/insights` | Computed analysis results | Profile |
| `/api/v1/fertility/export` | Data export/import | Profile |
| `/api/v1/fertility/devices` | Device integration management | Profile |
| `/api/v1/fertility/ws` | WebSocket for real-time updates | Profile |

### 7.3 Future Module Expansion

The API structure anticipates additional health modules:

```
/api/v1/fertility/...   (current)
/api/v1/sleep/...       (future)
/api/v1/nutrition/...   (future)
/api/v1/medication/...  (future)
```

Each module follows the same pattern: entries → insights → export.

---

## 8. Device Integration Approach

### 8.1 Adapter Pattern

```python
class DeviceAdapter(ABC):
    """Abstract interface for device integrations."""

    @abstractmethod
    async def connect(self) -> bool: ...
    @abstractmethod
    async def read_temperature(self) -> Optional[float]: ...
    @abstractmethod
    async def disconnect(self) -> None: ...
    @property
    @abstractmethod
    def device_info(self) -> DeviceInfo: ...
```

### 8.2 Initial Adapters

| Adapter | Technology | Priority |
|---|---|---|
| `HASensorAdapter` | Polls HA sensor entities (existing pattern) | Phase 1 |
| `ESPHomeAdapter` | ESPHome native API for custom BBT thermometers | Phase 3 |
| `BluetoothAdapter` | BLE thermometers via HA Bluetooth integration | Phase 3 |
| `ManualAdapter` | User manual entry (always available) | Phase 1 |

### 8.3 Device Data Flow

```
Device → Adapter → DeviceReading (raw)
                         │
                         ▼
                  Validation Layer (Pydantic)
                         │
                         ▼
                  TemperatureRecord (validated, stored)
                         │
                         ▼
                  Fertility Engine (analysis)
```

Raw device readings are stored separately from validated/logged temperatures. This preserves the raw data for debugging and allows re-validation if rules change.

---

## 9. ByrdOS Compatibility Strategy

### 9.1 Compatibility Principles

1. **No direct ByrdOS dependencies** during development
2. **Stable, documented APIs** that ByrdOS can consume
3. **Portable data models** (SQLAlchemy supports both SQLite and PostgreSQL)
4. **Clear service boundaries** — ByrdOS can swap any service independently
5. **Configuration-driven deployment** — same code, different config for HA vs. ByrdOS

### 9.2 What Changes for ByrdOS

| Aspect | HA Add-on | ByrdOS |
|---|---|---|
| Deployment | Docker container via HA Supervisor | Native service in ByrdOS |
| Auth | HA Ingress proxy | ByrdOS unified auth (OAuth2/OIDC) |
| Database | SQLite (single file) | PostgreSQL (scalable) |
| Config | bashio variables | ByrdOS config service / env vars |
| Devices | HA entity integration | Direct device adapters |
| Multi-user | Shared container, profile switching | Per-user isolated instances |
| Frontend | HA sidebar (Ingress) | Standalone PWA or ByrdOS app shell |
| Monitoring | HA add-on logs | ByrdOS centralized logging/monitoring |
| Updates | HA Add-on Store | ByrdOS package manager |

### 9.3 Migration Path to ByrdOS

1. All business logic is already in ByrdOS-compatible packages
2. Replace `HABridge` with `ByrdOSBridge` (same interface)
3. Swap database connection string
4. Swap auth middleware
5. Deploy as ByrdOS service

**Estimated migration effort:** Minimal — primarily configuration and bridge adapter replacement.

### 9.4 What Must NOT Be Done

- ❌ Import HA-specific libraries in business logic
- ❌ Use HA entity IDs as internal identifiers
- ❌ Rely on HA Supervisor for service lifecycle
- ❌ Use bashio for anything beyond config reading
- ❌ Hardcode HA paths (`/config/www`, `/data`)
- ❌ Assume single-user architecture

---

## 10. Technology Decision Summary

| Decision | Choice | Rationale |
|---|---|---|
| Web framework | FastAPI | Async, OpenAPI, Pydantic-native |
| Frontend framework | React + TypeScript | Component model, ecosystem |
| ORM | SQLAlchemy 2.0 | Mature, async, engine-agnostic |
| Database (HA) | SQLite (WAL) | Zero-config, local, sufficient |
| Database (ByrdOS) | PostgreSQL | Concurrent, scalable |
| API style | REST + WebSocket | CRUD + real-time |
| Validation | Pydantic v2 | Type-safe, FastAPI-native |
| Testing | pytest + pytest-asyncio | Industry standard |
| HA Card | Lit web component | HA ecosystem compatible |
| Build tool | Vite | Modern, fast |
| CSS | Tailwind CSS | Utility-first, design system |
| Package manager | uv / pip | Modern Python packaging |
| Type checking | mypy (strict) | Code quality |

---

## 11. ADRs to Create

These architectural decisions should be formalized as ADRs in `docs/adr/`:

| ADR # | Topic | Status |
|---|---|---|
| ADR-001 | Use FastAPI as the web framework | Proposed |
| ADR-002 | Use SQLAlchemy + Alembic for data layer | Proposed |
| ADR-003 | Separate HA Bridge as isolated service | Proposed |
| ADR-004 | Use React + TypeScript for web frontend | Proposed |
| ADR-005 | Use Lit for Lovelace card component | Proposed |
| ADR-006 | Data encryption at rest strategy | Proposed |
| ADR-007 | API versioning strategy | Proposed |
| ADR-008 | Database engine portability (SQLite → PostgreSQL) | Proposed |
| ADR-009 | Authentication and authorization model | Proposed |
| ADR-010 | Device integration adapter pattern | Proposed |

---

## 12. Security Architecture

### 12.1 Data Protection

| Layer | Mechanism |
|---|---|
| Transport | HTTPS (HA Ingress) / TLS (ByrdOS) |
| At Rest | AES-256-GCM per-profile encryption |
| Access | Profile-scoped queries, audit logging |
| Secrets | HA secrets / ByrdOS keychain, never in code |
| Export | Encrypted JSON with optional password protection |
| Backup | Encrypted database dumps |

### 12.2 Authentication

- **HA Add-on:** Relies on HA Ingress proxy (same as legacy) — acceptable for single-user
- **ByrdOS:** OAuth2/OIDC integration with ByrdOS unified auth
- **API access:** API key for HA automation scripts (scoped to specific actions)
- **Multi-profile:** Profile-level access control within the same deployment

### 12.3 Security Review Points

These must be reviewed before each phase:
1. Dependency audit (`pip-audit`, `npm audit`)
2. Secret management review
3. SQL injection check (mitigated by ORM)
4. XSS check (mitigated by React)
5. CSRF check (SPA tokens)
6. Rate limiting (multi-user only)
7. Input validation completeness
