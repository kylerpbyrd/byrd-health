# Session Handoff — 2026-07-26

## Project State

**Phase 2 Complete — Production Release Candidate 1**

The add-on is deployed and verified working on Home Assistant (`192.168.1.44:8123`). All milestones M-A through M-G are complete. M-F (Legacy Migration) was skipped — previous version had no users.

## What Was Done This Session

### Bug Fixes
- Fixed ingress path resolution — HA strips prefix before forwarding, IngressMiddleware now always sets `script_name`
- Fixed Vite base path — changed from `/` to `./` for relative asset URLs that work through HA ingress proxy
- Fixed `test_delete_profile` flaky test — now explicitly activates Keep profile before deleting Remove

### Features Delivered
- **HA Bridge wired** — entity publishing on startup, after entry creation, after reanalysis. 9 entities per profile published to HA.
- **Encryption at rest** — AES-256-GCM per-profile. Auto-generated persistent secret key (no hardcoded defaults). Sensitive fields encrypted: temps, signs, symptoms, notes, discard_reason.
- **Frontend polish** — ErrorBoundary, sonner toasts, skeleton loaders, empty states, accessibility (skip-to-content, aria labels).
- **Test coverage** — 160 Python + 65 frontend = 225 total tests. All passing.
- **Documentation** — User guide, feature guide, troubleshooting, changelog, developer guide, architecture overview.
- **Phase 3 plan** — ADR-0011 (Device Adapter Pattern), ADR-0012 (WebSocket Architecture), `PHASE3_PLAN.md`.

### Architecture Changes
- Created `packages/web_api/src/web_api/ingress.py` — single ingress abstraction (`IngressMiddleware` + `get_application_prefix()`)
- Created `packages/data_service/src/data_service/encryption.py` — `ProfileEncryption` class
- Updated `AGENTS.md` — separated Architect and Release Engineer responsibilities, added milestone handoff workflow
- Added `docs/archive/` — 7 completed planning documents moved out of active docs
- Updated `README.md` — current status, architecture, features

## Key Files to Know

| File | Purpose |
|---|---|
| `packages/web_api/src/web_api/ingress.py` | Ingress middleware + `get_application_prefix()` |
| `packages/web_api/src/web_api/app.py` | FastAPI app, lifespan with HA Bridge wiring |
| `packages/data_service/src/data_service/encryption.py` | AES-256-GCM encryption |
| `packages/data_service/src/data_service/repositories.py` | Encrypt/decrypt in EntryRepository |
| `frontend/vite.config.ts` | `base: "./"` for relative assets |
| `frontend/src/lib/api.ts` | `API_BASE` reads `window.__INGRESS_PATH__` |
| `frontend/src/App.tsx` | `BrowserRouter basename` from `__INGRESS_PATH__` |
| `run.sh` | Auto-generates encryption key, bashio config |
| `config.yaml` | HA add-on metadata, ingress config |
| `AGENTS.md` | Agent responsibilities and operating principles |

## Current Architecture

```
fertility_engine (pure Python, no deps)
       ↑
data_service (SQLAlchemy + encryption)
       ↑
web_api (FastAPI, ingress, lifespan)
       ↑
ha_bridge (HA entity publishing — isolated boundary)
       
frontend (React + Vite + Tailwind)
```

## Known Issues (Non-Blocking)

1. **ADR-0006 partial violation** — `web_api/app.py` imports `HABridge` directly instead of through `HABridgeProtocol`. The protocol should be implemented in Phase 3 alongside ADR-0011/0012.
2. **Mypy path conflict** — `__init__.py` files added for pytest collection confuse mypy. Needs `--explicit-package-bases` flag.
3. **Frontend chunk size** — main bundle is ~700KB (warns at >500KB). Code splitting deferred to Phase 3.
4. **npm audit** — 7 vulnerabilities in dev dependencies (standard for React ecosystem, non-blocking).

## What's Next

### Phase 3 (requires user approval of ADR-0011 and ADR-0012)

The Phase 3 plan is in `docs/PHASE3_PLAN.md`. Key milestones:

1. **P3-M1: Device Adapter Infrastructure** — Create `packages/device_adapters/` with `DeviceAdapter` protocol + `DeviceRegistry`
2. **P3-M2: WebSocket Infrastructure** — `WebSocketBroker` pub/sub, `/ws` endpoint, real-time device readings
3. **P3-M3: ESPHome Integration** — Native API client adapter
4. **P3-M4: Bluetooth Thermometer Integration** — BLE GATT adapter for BBT thermometers
5. **P3-M5: Frontend Real-Time** — WebSocket client, live dashboard, auto-fill from device

### Quick Wins (if not starting Phase 3 yet)

1. Implement `HABridgeProtocol` per ADR-0006 — remove direct ha_bridge import from web_api
2. Fix mypy path conflict with `--explicit-package-bases`
3. Code-split frontend bundle (lazy-load pages)

## Graphify Reference

- `graph/index.json` — master index
- `graph/edges.json` — relationship graph (344 lines)
- `graph/nodes/services/` — per-service metadata

## Documentation Map

| Doc | Audience |
|---|---|
| `README.md` | Everyone |
| `docs/USER_GUIDE.md` | End users |
| `docs/FEATURES.md` | Users learning features |
| `docs/TROUBLESHOOTING.md` | Users with issues |
| `docs/ARCHITECTURE.md` | Developers |
| `docs/DEVELOPER_GUIDE.md` | Developers |
| `docs/MILESTONE_GUIDE.md` | Project planning |
| `docs/PHASE3_PLAN.md` | Future roadmap |
| `docs/adr/` | Architecture decisions (12) |
| `docs/archive/` | Completed planning (7 docs) |
| `CHANGELOG.md` | Version history |

## Agent Directives

- `AGENTS.md` — Shared agent responsibilities
- `.opencode/agents/architect.md` — Architect operating directive (local only, gitignored)

## Release Engineer

Per updated directive, the Architect does NOT self-certify releases. Completed milestones must be handed to the Release Engineer for validation before advancing.

---

**Next session starter:** Review `docs/MILESTONE_GUIDE.md` for current progress, then either approve Phase 3 ADRs (0011, 0012) or pick a quick win.
