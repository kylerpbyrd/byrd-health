# Developer Setup Guide — Byrd Health

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.12+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.40+ | `git --version` |

Optional but recommended:

- [uv](https://docs.astral.sh/uv/) — faster pip alternative
- [Visual Studio Code](https://code.visualstudio.com/) with Python and TypeScript extensions

---

## Repository Structure

```
byrd-health/
├── packages/
│   ├── fertility_engine/     # Pure algorithm package (pip-installable)
│   ├── data_service/         # Database models, migrations, repositories
│   └── web_api/              # FastAPI REST + WebSocket service
├── frontend/                 # React SPA (Vite + TypeScript)
├── docs/                     # Project documentation
│   └── adr/                  # Architecture Decision Records
├── graph/                    # Graphify knowledge graph
├── legacy/                   # Legacy application (reference only)
├── tools/                    # Utility scripts (e.g., legacy migration)
├── AGENTS.md                 # Agent workflow and project principles
├── PROJECTPLAN.md            # Master project plan and phases
└── pyproject.toml            # Root project config (test, lint, typecheck)
```

---

## Setup

### 1. Clone Repository

```bash
git clone <repo-url>
cd byrd-health
```

### 2. Create Python Virtual Environment

```bash
python -m venv .venv
```

**Windows:**
```powershell
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Python Packages

Install all three packages in editable mode:

```bash
pip install -e packages/fertility_engine -e packages/data_service -e packages/web_api
```

Install dev dependencies (testing, linting, type checking):

```bash
pip install -e ".[dev]"
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running Locally

### Start the Backend

```bash
cd packages/web_api
uvicorn src.web_api.app:create_app --reload --host 127.0.0.1 --port 8000
```

The API is available at **http://localhost:8000**. OpenAPI docs at **http://localhost:8000/docs**.

### Start the Frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

The frontend dev server starts at **http://localhost:5173** and proxies API requests to the backend.

### Access the Application

Open **http://localhost:5173** in your browser.

---

## Running Tests

### Python Tests

```bash
# All packages
pytest

# Specific package
pytest packages/fertility_engine
pytest packages/data_service
pytest packages/web_api

# With coverage
pytest --cov=packages --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test                # Run once
npm run test:watch      # Watch mode
```

---

## Linting

```bash
# Python (ruff)
ruff check .

# Auto-fix
ruff check --fix .

# Format
ruff format .
```

```bash
# Frontend (TypeScript)
cd frontend
npm run lint
```

---

## Type Checking

```bash
# Python (mypy — strict mode)
mypy packages/
```

```bash
# Frontend (TypeScript)
cd frontend
npm run typecheck
```

---

## Pre-commit Hooks

Install pre-commit hooks for automatic linting and type checking on commit:

```bash
pre-commit install
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/byrd_health.db` | Database connection URL |
| `BYRD_ENV` | `development` | Environment: `development`, `production` |
| `BYRD_LOG_LEVEL` | `INFO` | Logging level |
| `BYRD_CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins (comma-separated) |
| `BYRD_SECRET_KEY` | *(auto-generated)* | Secret key for session management |

For production deployment (Phase 2+), additional variables control encryption keys and HA integration.

---

## Common Issues

**ModuleNotFoundError for `fertility_engine` or `data_service`**
Run `pip install -e packages/fertility_engine -e packages/data_service -e packages/web_api` to ensure packages are installed in editable mode.

**Frontend can't reach the API**
Check the Vite proxy config in `frontend/vite.config.ts` and ensure the backend is running on port 8000.

**Database is locked (SQLite)**
Only occurs with concurrent write-heavy access. Stop the running backend and restart. For development this should be rare.

---

## Further Reading

- [PHASE1_PLAN.md](PHASE1_PLAN.md) — Phase 1 implementation plan
- [ARCHITECTURE.md](ARCHITECTURE.md) — Platform architecture overview
- [adr/](adr/) — Architecture Decision Records
