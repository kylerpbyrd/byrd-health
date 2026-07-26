# Session Handoff — VS-1 Runtime Validation (2026-07-26)

> **Summary:** Add-on starts, UI loads, profiles can be created. Submitting a temperature entry hangs indefinitely (POST timeout). Backend never receives the request.

---

## What's Working

| Feature | Status | Evidence |
|---------|--------|----------|
| Docker image builds (CI) | ✅ | GHCR: `ghcr.io/kylerpbyrd/byrd-health-fertility:main` |
| Ruff lint (CI) | ✅ | All checks pass |
| Mypy type check (CI) | ✅ | 53 source files, no issues |
| Pytest (CI) | ✅ | 262 tests pass |
| HA Supervisor install | ✅ | Image pulls, add-on installs |
| Add-on startup | ✅ | No errors, clean logs |
| Encryption key generation | ✅ | `/data/.byrd_key` created |
| Database tables created | ✅ | `create_all()` in lifespan succeeds |
| UI loads via Ingress | ✅ | All 7 pages render |
| Profile creation (API) | ✅ | `POST /profiles/` → 201 |
| Profile activation | ✅ | `POST .../activate` → 200 |
| Insights API | ✅ | `GET /insights/` → 200 |
| Cycles API | ✅ | `GET /cycles/current` → 200 |
| Entry form renders | ✅ | Log Entry page loads with all fields |
| Frontend assets | ✅ | All JS/CSS chunks load (304s) |

## What's NOT Working

| Issue | Status | Details |
|-------|--------|---------|
| **POST /entries/ hangs** | ❌ BLOCKING | Request times out. Backend never receives it (no log line). |
| WebSocket connections | ⚠️ Non-blocking | HA Ingress doesn't proxy WS. Reconnects endlessly. |
| HA entity publishing | ⚠️ Not verified | Entities may not appear yet |
| Chart 404 | ⚠️ Expected | No temperature data to chart |

## The POST /entries/ Hanging Issue — Full Diagnostics

### Tests Performed

1. **Browser submit** — "Save Entry" button clicked. No response. Network tab shows request sent but no status code (hung).
2. **curl via Ingress** — `Invoke-RestMethod` with `-TimeoutSec 10`. Timed out. No response.
3. **HA Log check** — Filtered for `POST` and `entries`. No `POST /entries/` line appears. Request never reaches the backend.
4. **GET requests work** — `GET /api/v1/fertility/entries/today` returns 200. `GET /profiles/` returns 200. Only POST hangs.

### What the frontend payload looks like

```json
{
  "date": "2026-07-26",
  "temp_value": 97.4,
  "is_discarded": false,
  "discard_reason": "",
  "menstrual_flow": "",
  "cervical_mucus": "",
  "cervical_position": "",
  "cervical_firmness": "",
  "cervical_opening": "",
  "opk_result": "not_tested",
  "symptoms": [],
  "is_period_start": false,
  "notes": ""
}
```

### Theories to Investigate

1. **HA Ingress proxy + POST body size/encoding** — The Ingress proxy may handle GET fine but choke on POST bodies. Test: curl GET first to confirm token works, then compare POST behavior.

2. **`Content-Length` mismatch** — The frontend sends `Content-Type: application/json` but HA Ingress may require `Transfer-Encoding: chunked` or specific content-length headers.

3. **Encryption hang** — `create_entry` in `entries.py` calls `entries.upsert_temperature()` which encrypts the temp_value. If the encryption key is missing or the cryptography library hangs, the request would block.

4. **HA Bridge lifecycle** — `create_entry` calls `bridge.publish_insights()` which talks to HA Supervisor API. If that hangs, the entire request hangs with it. The lifespan already logged "Lovelace resources API not available (YAML mode?)" — the Supervisor API call might be the culprit.

5. **Session/transaction deadlock** — `get_or_create_current` in the cycle repository creates a cycle with `session.flush()`. If there's a transaction conflict with the lifespan-initiated session, it could deadlock.

### Quick Diagnostic Commands

Test if ANY POST works through Ingress:
```powershell
# Test POST to profiles (already known to work)
Invoke-RestMethod -Uri "http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/api/v1/fertility/profiles/" -Method POST -ContentType "application/json" -Body '{"name":"test"}'
```

Test if the health endpoint works:
```powershell
Invoke-RestMethod -Uri "http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/api/health"
```

Curl from the HA host itself (bypasses Ingress):
```bash
# On HAOS terminal
curl -X POST http://localhost:8000/api/v1/fertility/entries/ \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-07-26","temp_value":97.4,"opk_result":"not_tested","symptoms":[],"is_period_start":false,"notes":""}'
```

### Most Likely Cause

The `create_entry` function in `entries.py` line 140-158 calls `bridge.publish_insights()` AFTER saving data. This calls `HABridge._check_notifications()` which tries to communicate with the HA Supervisor API. If the Supervisor API call hangs (which it might — the lifespan already logged it was unavailable), the entire request hangs.

**Quick fix to test:** Comment out lines 148-158 in `entries.py` (the bridge.publish_insights call). If the entry then works, the bridge is the culprit.

---

## Architecture Decisions Made in This Session

| Decision | Document |
|----------|----------|
| OCI container distribution via GHCR | `docs/adr/ADR-0013-home-assistant-container-distribution.md` |
| Phase A audit remediation plan | `docs/audits/AUDIT_RESPONSE.md` |
| Image-based add-on (no Dockerfile build) | `docs/plans/ADDON_CONTAINER_MIGRATION_PLAN.md` |

## Key File Changes (Recent)

| File | Change |
|------|--------|
| `packages/web_api/src/web_api/app.py` | `create_all()` replaces alembic; container path fixes |
| `packages/ha_bridge/src/ha_bridge/config.py` | TYPE_CHECKING + runtime import for HABridgeConfig |
| `run.sh` | Removed alembic call (timing issue); `${BYRD_SECRET_KEY:-}` fix |
| `frontend/src/lib/api.ts` | Symptom payload fix; createCycle body fix |
| `frontend/src/pages/SettingsPage.tsx` | Date picker for new cycle |
| `pyproject.toml` | Mypy/ruff config; B008 ignore; per-file-ignores |
| `.github/workflows/container-build.yml` | CI pipeline to GHCR |
| `packages/*/src/*/py.typed` | Type marker files (5 packages) |
| `packages/*/tests/__init__.py` | Removed (4 of 5) to fix conftest collision |
| `repository/byrd_health_fertility/config.yaml` | Added `image:` key |

## Current State of the Image

- Image: `ghcr.io/kylerpbyrd/byrd-health-fertility:main`
- Latest commit: `ceeda49`
- CI: All checks pass (ruff, mypy, pytest 262)

---

## Next Steps for Debugging

1. **Isolate whether it's Ingress or Backend** — run curl from inside the HA container (bypass Ingress)
2. **Test POST /profiles/** — confirms POST works through Ingress generally
3. **Comment out bridge.publish_insights()** in entries.py — test if bridge is the hang
4. **Check for Python-level hang** — if request reaches backend but hangs, add logging to trace where
5. **Check the frontend** — verify the browser actually sends the POST (Network tab → filter entries)
