# Byrd Health

Privacy-first personal health intelligence platform.

## Status

**Phase 1 — Platform Foundation (in progress)**

Four core services are being built: Fertility Engine, Data Service, Web API, and Web Frontend. No Home Assistant integration yet — pure platform only.

---

## Architecture

Byrd Health is a **service-oriented platform** with four Phase 1 packages:

| Package | Description | Technology |
|---|---|---|
| `fertility_engine` | Sympto-thermal fertility algorithms | Pure Python, Pydantic |
| `data_service` | Database models, migrations, CRUD | SQLAlchemy 2.0 + Alembic |
| `web_api` | REST + WebSocket API gateway | FastAPI + Uvicorn |
| `web_frontend` | User interface and charting | React + TypeScript + Recharts |

Future services (Phase 2-3): HA Bridge, Device Adapters.

---

## Quick Start

**Prerequisites:** Python 3.12+, Node 20+

```bash
# Clone
git clone <repo-url>
cd byrd-health

# Python environment
python -m venv .venv
.venv\Scripts\activate

# Install packages
pip install -e packages/fertility_engine -e packages/data_service -e packages/web_api

# Install frontend dependencies
cd frontend && npm install

# Run backend
cd packages/web_api && uvicorn src.web_api.app:create_app --reload

# Run frontend (separate terminal)
cd frontend && npm run dev
```

Access at **http://localhost:5173**

---

## Documentation

| Document | Description |
|---|---|
| [PHASE1_PLAN.md](docs/PHASE1_PLAN.md) | Phase 1 implementation milestones |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Platform architecture overview |
| [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Developer setup and workflows |
| [LEGACY_REVIEW.md](docs/LEGACY_REVIEW.md) | Legacy application analysis |
| [ARCHITECTURE_RECOMMENDATIONS.md](docs/ARCHITECTURE_RECOMMENDATIONS.md) | Detailed architecture recommendations |
| [adr/](docs/adr/) | Architecture Decision Records (10 ADRs) |

---

## Development Philosophy

Byrd Health follows:

- Architecture-first development.
- Agent-assisted engineering.
- Graphify knowledge management.
- Privacy-first design.
