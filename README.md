# Byrd Health

Privacy-first, self-hosted fertility intelligence platform. Deployed as a Home Assistant Add-on. Architected for future ByrdOS migration.

**Status:** Phase 2 — Production Release Candidate

---

## Quick Start (Home Assistant)

1. Add the Byrd Health repository to your Home Assistant Add-on Store
2. Install **Byrd Health — Fertility Tracker**
3. Start the add-on and open the Web UI
4. Create a profile and log your first temperature

[Full Installation Guide →](docs/USER_GUIDE.md)

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Byrd Health Platform                    │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │ Web Frontend │  │  HA Bridge   │                      │
│  │ (React SPA)  │  │  (Entities)  │                      │
│  └──────┬───────┘  └──────┬───────┘                      │
│         │                 │                               │
│         ▼                 ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                Web API (FastAPI)                     │ │
│  └──────────┬──────────────────────┬───────────────────┘ │
│             │                      │                      │
│             ▼                      ▼                      │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │ Fertility Engine │  │       Data Service            │  │
│  │  (Pure Python)   │  │  (SQLAlchemy + Encryption)    │  │
│  └──────────────────┘  └──────────────┬───────────────┘  │
│                                       │                   │
│                                       ▼                   │
│                           ┌──────────────────────┐       │
│                           │  SQLite (encrypted)  │       │
│                           └──────────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

**Five packages, clean boundaries:**
- `fertility_engine` — Sympto-thermal algorithms (zero dependencies)
- `data_service` — Database layer with AES-256-GCM encryption
- `web_api` — FastAPI REST gateway with Ingress support
- `ha_bridge` — Home Assistant entity publishing (isolated)
- `frontend` — React + TypeScript + Tailwind SPA

---

## Features

- Basal body temperature tracking (F/C)
- Cycle phase detection (menstrual, pre-ovulatory, fertile, luteal)
- Ovulation detection with 3-day temperature shift confirmation
- Fertile window prediction using sympto-thermal method
- BBT chart with coverline, phase shading, and ovulation markers
- Multi-profile support
- 9 Home Assistant entities per profile
- Data export (JSON)
- Encrypted at rest (AES-256-GCM, per-profile keys)
- Privacy-first — all data stored locally, never leaves the device

[Full Feature Guide →](docs/FEATURES.md)

---

## Development

```bash
# Prerequisites: Python 3.12+, Node 20+

# Install Python packages
pip install -e packages/fertility_engine
pip install -e packages/data_service
pip install -e packages/web_api
pip install -e packages/ha_bridge

# Start backend
uvicorn web_api.app:create_app --factory --reload --port 8000

# Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Access at **http://localhost:5173** (frontend dev server proxies `/api` to backend).

[Developer Guide →](docs/DEVELOPER_GUIDE.md)

---

## Testing

```bash
# All 160 Python tests (root-level)
pytest

# 65 frontend tests
cd frontend && npm test
```

---

## Documentation

| Document | Audience |
|---|---|
| [User Guide](docs/USER_GUIDE.md) | End users installing on Home Assistant |
| [Feature Guide](docs/FEATURES.md) | Users learning sympto-thermal tracking |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Users with common issues |
| [Architecture](docs/ARCHITECTURE.md) | Developers understanding the platform |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | Developers setting up locally |
| [Milestone Guide](docs/MILESTONE_GUIDE.md) | Project roadmap and progress |
| [Phase 3 Plan](docs/PHASE3_PLAN.md) | Device integration roadmap |
| [ADR Index](docs/adr/) | Architecture Decision Records (12) |
| [Changelog](CHANGELOG.md) | Version history |

---

## Privacy

All health data is stored locally in an encrypted SQLite database. Data never leaves your device. No cloud dependencies. No telemetry. No accounts. You own your data.

---

## License

MIT
