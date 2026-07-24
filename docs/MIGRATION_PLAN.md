# Migration Plan — Legacy to Byrd Health

> Each major component from the legacy BBT Fertility Tracker is classified and a migration strategy is provided.
>
> Classifications: **KEEP** | **REFACTOR** | **REWRITE** | **REMOVE**

---

## 1. Classification Summary

| Classification | Count | Strategy |
|---|---|---|
| KEEP (concept/logic) | 5 | Preserve algorithmic logic and design patterns; rewrite implementation |
| REFACTOR | 6 | Retain with structural improvements, modern tooling |
| REWRITE | 7 | Complete redesign with new architecture |
| REMOVE | 3 | No longer needed |

---

## 2. Component-by-Component Decisions

### 2.1 Algorithms Package (`app/algorithms/`)

**Decision: KEEP (concept/logic), REWRITE (implementation)**

**Components:**
- `coverline.py` — Coverline calculation
- `ovulation.py` — Ovulation detection (standard, conservative, witch's hat)
- `fertile_window.py` — Fertile window + cycle phase
- `cycle_analysis.py` — Analysis orchestrator

**Reasoning:**

These modules represent the **most valuable intellectual property** in the legacy codebase. They are:

- Pure functions with no framework dependencies
- Well-typed inputs/outputs (dataclasses, typed dicts)
- Scientifically grounded in the sympto-thermal method
- Already partially tested
- Directly portable to any Python framework

**Migration strategy:**

1. Extract the algorithmic logic into a standalone `fertility_engine` Python package (pip-installable)
2. Replace raw dict inputs with Pydantic models for type safety and validation
3. Add comprehensive edge-case tests (missing readings, irregular cycles, boundary conditions)
4. Remove the database dependency from `cycle_analysis.py` — make it a pure function that receives data and returns insights
5. Move persistence logic to a separate `DataService`
6. The orchestrator (`cycle_analysis.py`) should be split: analysis logic stays in the engine; DB upsert logic moves to the data layer

**Interface contract:**
```python
# Input models
class TemperatureRecord(BaseModel): ...
class FertilitySignRecord(BaseModel): ...

# Pure function
def analyze_cycle(temps: list[TemperatureRecord], signs: list[FertilitySignRecord],
                  profile_settings: ProfileSettings) -> CycleInsights: ...

# Result model
class CycleInsights(BaseModel): ...
```

---

### 2.2 `app/db.py` — Database Module

**Decision: REWRITE**

**Reasoning:**

The raw SQL approach served the monolithic Flask app well for its scope, but:

- No ORM → No type safety, no migration tooling, string-heavy queries
- SQLite-specific SQL → not portable to PostgreSQL for ByrdOS
- Schema versioning exists as a framework but is unused (only a placeholder migration)
- Connection management with `check_same_thread=False` is a Flask workaround

**Migration strategy:**

1. Replace raw `sqlite3` with **SQLAlchemy 2.0** (async-capable ORM)
2. Add **Alembic** for proper forward/reverse migrations
3. Define all models as SQLAlchemy declarative classes
4. Keep SQLite as the default engine for HA Add-on deployment
5. Design models to be engine-agnostic (work with SQLite now, PostgreSQL later)
6. Add data encryption at rest (SQLite SEE or application-layer encryption)

**Preserved:**
- The conceptual schema (tables, relationships, constraints) — it is well-designed
- WAL journal mode pattern
- Foreign key cascading behavior

---

### 2.3 `app/app.py` — Flask Application

**Decision: REWRITE**

**Reasoning:**

The 994-line Flask monolith is the primary architectural limitation. It combines:

- Route definitions (dashboard, entry, history, profiles, settings, API)
- Request lifecycle management (DB open/close, profile resolution, CSRF)
- Background task management (thread-based analysis, sensor polling)
- Startup initialization (DB init, Lovelace card install, entity publishing)
- Business logic (cycle closing, phase calculation inline in routes)

**Migration strategy:**

Split into **five separate services:**

| New Service | Responsibility |
|---|---|
| `web_api` | FastAPI REST + WebSocket endpoints |
| `fertility_engine` | Pure algorithm package (see 2.1) |
| `data_service` | Database access layer (see 2.2) |
| `ha_bridge` | Home Assistant integration (see 2.5) |
| `web_frontend` | React/Lit SPA (see 2.7) |

**Key architectural changes:**
- Async throughout (FastAPI + async SQLAlchemy)
- Background tasks via proper task queue (e.g., Celery or simple asyncio tasks for single-user)
- Startup logic moves to service entrypoints, not route handlers
- Dependency injection for services rather than Flask `g` object
- Structured logging with correlation IDs

**Preserved:**
- Route URL structure (can be mapped 1:1 initially for HA automation compatibility)
- CSRF protection pattern (adapt for SPA)
- Export format (`bbt-fertility-tracker-export` v1)

---

### 2.4 `app/validation.py` — Input Validation

**Decision: KEEP (logic), REFACTOR (implementation)**

**Reasoning:**

The validation module is clean, well-structured, and has acceptable enum sets. However:

- Custom validation functions should be replaced with **Pydantic** models
- Valid value sets (`FLOW_VALUES`, `MUCUS_VALUES`, etc.) should become Python enums
- Temperature range validation should be configurable per-unit in Pydantic validators

**Migration strategy:**

1. Convert all value sets to `enum.StrEnum` classes
2. Create Pydantic models for each request/input type
3. Keep the validation logic in custom Pydantic validators where needed
4. The `validation.py` file itself is removed; its logic migrates into models

---

### 2.5 `app/ha_client.py` — Home Assistant Client

**Decision: REWRITE**

**Reasoning:**

The HA client has a clean separation from the Flask app and is functionally complete. However:

- Uses synchronous `urllib` HTTP calls — should be async (`httpx`/`aiohttp`)
- Entity publishing is hardcoded to specific entity IDs — should be config-driven
- Lovelace card registration is coupled to hardcoded URLs
- Sensor polling uses `threading.Timer` — should use `asyncio`
- No WebSocket connection for real-time updates

**Migration strategy:**

1. Rewrite as an **async HA Bridge** service
2. Use `httpx` for async HTTP to HA REST API
3. Add WebSocket connection for real-time entity state monitoring
4. Make entity definitions configurable — driven by a schema, not hardcoded
5. Move Lovelace card registration logic into the add-on's startup script, not the app code
6. Isolate ALL Home Assistant-specific code in this service — nothing else should import from HA
7. Add proper retry logic with exponential backoff

**Interface contract:**
```python
class HABridge:
    async def publish_insights(self, profile_slug: str, insights: CycleInsights) -> None
    async def poll_sensor(self, entity_id: str) -> Optional[float]
    async def register_lovelace_resource(self, url: str) -> None
```

---

### 2.6 `app/app.py` — Background Tasks

**Decision: REWRITE**

**Reasoning:**

The legacy app uses `threading.Thread(daemon=True)` for background analysis and `threading.Timer` for sensor polling. This pattern has several problems:

- No error recovery — if analysis crashes, it's silently lost
- No task queue — concurrent analyses can create database contention
- No monitoring — can't see task status or history
- Daemon threads die silently on process shutdown

**Migration strategy:**

1. For the HA Add-on (single-user): Use FastAPI's `BackgroundTasks` for simple fire-and-forget, or a lightweight `asyncio.create_task` pattern
2. For future ByrdOS (multi-user): Use a proper task queue (Celery, ARQ, or Dramatiq)
3. Sensor polling becomes an `asyncio` loop with configurable interval
4. Add task status tracking (queued → running → complete/failed)
5. Add structured logging per task with correlation IDs

---

### 2.7 Templates (`app/templates/`) — Web UI

**Decision: REWRITE**

**Reasoning:**

The Jinja2 templated UI served its purpose for a v1 add-on but:

- Server-rendered pages require full page reloads
- Tightly coupled to Flask (Flask-specific template globals, `url_for`, `g`)
- No component reusability across pages
- No offline capability
- Not accessible (no ARIA labels, limited keyboard navigation)
- Cannot be shared between HA Add-on and future ByrdOS deployment

**Migration strategy:**

1. Build a **React SPA** (or **Lit** for web components) as a standalone frontend
2. Use Chart.js directly in React components (or consider ECharts/D3 for more control)
3. Bundle as static assets served by the backend or a separate static file server
4. The Lovelace card (`bbt-card.js`) remains a standalone web component (Lit-based rewrite)
5. Implement PWA features for offline access
6. Add proper accessibility (WCAG 2.1 AA target)
7. Use a design system for consistency across future health modules

**Preserved:**
- UI layout patterns (dashboard with phase banner + stats + chart; entry form layout)
- Color scheme concept (phase-based coloring)
- Data visualization approach (annotated line chart)

---

### 2.8 Static Assets (`app/static/`)

**Decision: REWRITE (CSS/JS), KEEP (concept)**

**Reasoning:**

- `chart-init.js`: Chart.js initialization logic is sound but should be integrated into React components
- `bbt-card.js`: The Lovelace web component works well but should be rewritten in **Lit** for better HA compatibility and maintainability
- `app.css`: The CSS is well-organized with custom properties but will be replaced by component-scoped styles in React or a CSS-in-JS solution
- Chart.js library files: Bundling approach is correct but should use proper dependency management (npm) rather than `wget` in Dockerfile

**Migration strategy:**

1. Move Chart.js to npm dependency management
2. Rewrite `chart-init.js` as React hooks/components
3. Rewrite `bbt-card.js` in Lit with TypeScript
4. Replace `app.css` with Tailwind CSS or CSS Modules
5. Chart.js annotation plugin remains but managed via npm

---

### 2.9 Test Suite (`tests/`)

**Decision: REFACTOR**

**Reasoning:**

The existing tests are too few (11 total) but well-structured:

- `test_routes.py` properly uses `pytest` fixtures with isolated databases
- `test_algorithms.py` tests cover key algorithmic paths
- The test infrastructure (tmp_path, monkeypatch, isolated DB) is sound

**Migration strategy:**

1. Expand test coverage significantly (target: 80%+ line coverage)
2. Write integration tests for the API layer
3. Write comprehensive algorithm tests for all edge cases
4. Add property-based testing for fertility algorithms
5. Add performance benchmarks for analysis pipeline
6. Migrate to `pytest-asyncio` for async service tests
7. Add contract tests for HA Bridge integration

---

### 2.10 HA Add-on Configuration (`config.yaml`, `run.sh`, `Dockerfile`)

**Decision: REFACTOR**

**Reasoning:**

These files define the HA Add-on packaging and are functionally correct. They need updating for the new architecture, not fundamental redesign.

**Migration strategy:**

- `config.yaml`: Update name/description/version, add new configuration options (API keys, WebSocket port, data encryption toggle), keep the HA add-on metadata structure
- `Dockerfile`: Modernize (use Python 3.12+, install dependencies via pip from requirements.txt rather than individual wget calls, use multi-stage build for frontend), bundle frontend build artifacts
- `run.sh`: Update to start the new FastAPI service with uvicorn rather than `python3 app.py`, keep bashio config reading pattern
- `repository.yaml`: Update URL to new repository

---

### 2.11 CI/CD Pipeline (`.github/workflows/ci.yml`)

**Decision: REFACTOR**

**Reasoning:**

The CI pipeline covers tests, linting, YAML validation, and Docker build — all good patterns to retain. It needs expansion for the new stack.

**Migration strategy:**

1. Add frontend build step (npm install + build)
2. Add TypeScript type checking
3. Add Python type checking (mypy)
4. Add security scanning (bandit for Python, npm audit for JS)
5. Add Docker image scanning (Trivy)
6. Keep YAML validation and add-on config validation
7. Add release automation (semantic versioning)

---

### 2.12 Documentation (`legacy/docs/`, `README.md`, `ROADMAP.md`)

**Decision: KEEP (reference), REWRITE (user-facing)**

**Reasoning:**

The legacy documentation is high quality and should be preserved as reference material for the migration. New user-facing documentation must reflect the new architecture.

**Migration strategy:**

1. Archive legacy docs in `docs/legacy-archive/` for reference
2. Create new user documentation for Byrd Health Fertility Service
3. Create developer documentation for the new modular architecture
4. Create ADRs for all architectural decisions
5. The legacy ROADMAP's milestone structure provides a good template for the new project roadmap

---

### 2.13 Lovelace Card (`app/static/js/bbt-card.js`)

**Decision: REFACTOR**

**Reasoning:**

The Lovelace card is a functional web component that displays BBT data well. It needs modernization but the concept is proven.

**Migration strategy:**

1. Rewrite in **Lit** (TypeScript) for better HA ecosystem compatibility
2. Use the new API endpoints rather than directly reading HA entity states
3. Make it configurable via HA's standard card configuration
4. Add more data points (mini chart, trend indicators)
5. Publish as a separate HACS-compatible component

---

### 2.14 Legacy-Specific Files to REMOVE

| File/Directory | Reason |
|---|---|
| `legacy/AGENTS.md` | Legacy agent hierarchy superseded by Byrd Health's agent system |
| `legacy/PROMPT.md` | Legacy architect prompt superseded by `.opencode/agents/architect.md` |
| `legacy/byrdos/README.md` | Placeholder description — ByrdOS concept is now in PROJECTPLAN.md |
| `legacy/app/requirements.txt` (flask==3.0.3) | Flask replaced by FastAPI |
| Legacy data directory pattern (`/data/bbt.db`) | Keep the concept but use new schema with Alembic migrations |

---

## 3. Migration Ordering

### Phase 1 — Foundation (current)
1. Extract algorithm logic into standalone `fertility_engine` package
2. Define Pydantic models (replacing raw dicts)
3. Set up SQLAlchemy + Alembic (replacing raw SQL)
4. Write comprehensive algorithm tests

### Phase 2 — Backend
5. Build FastAPI web API (replacing Flask routes)
6. Build async HA Bridge (replacing `ha_client.py`)
7. Build Data Service layer
8. Integrate fertility engine with data service

### Phase 3 — Frontend
9. Build React SPA (replacing Jinja2 templates)
10. Rewrite Lovelace card in Lit
11. Integrate with new API

### Phase 4 — Packaging
12. Update Dockerfile, run.sh, config.yaml
13. Test full HA Add-on deployment
14. Update CI/CD pipeline

### Phase 5 — Polish
15. Expand test coverage
16. Add monitoring and health checks
17. Document API and developer guides

---

## 4. Data Migration Strategy

Existing user data in `/data/bbt.db` must be migratable to the new schema.

**Approach:**
1. Create an Alembic migration that reads the legacy schema and transforms it to the new schema
2. Map legacy tables → new models (the schema is fundamentally similar)
3. Preserve all historical data (temperatures, signs, cycles, profiles)
4. Add a migration flag so the new system can detect legacy DB and offer migration
5. Keep the legacy export format (`bbt-fertility-tracker-export` v1) as a supported import format
6. Test migration with real-world data before release

---

## 5. Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Data loss during migration | Critical | Extensive migration testing, backup-first approach, dry-run mode |
| Breaking HA automations | High | Maintain same entity IDs and API response shapes initially |
| Algorithm behavior changes | High | Preserve exact algorithm logic; comprehensive regression tests |
| Performance regression | Medium | Benchmark legacy vs. new; async should improve performance |
| User confusion during upgrade | Medium | Clear upgrade notes, automatic data migration, rollback path |
