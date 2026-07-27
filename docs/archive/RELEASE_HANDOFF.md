# Phase 2 RC1 — Release Handoff

> **From:** Lead Architect  
> **To:** Release Engineer  
> **Date:** 2026-07-25  
> **Status:** Ready for validation

---

## 1. Handoff Summary

Phase 2 milestones M-A through M-G are complete. RC1 is deployed on Home Assistant at `192.168.1.44:8123`. This is a formal handoff to the Release Engineer for independent validation per AGENTS.md.

Per operating principles: **The Architect does NOT self-certify releases.** The Release Engineer returns a pass/fail verdict with evidence. The Architect will not advance to Phase 3 until release validation passes.

---

## 2. What to Validate

### 2.1 Docker Build

```bash
docker build -t byrd-health:rc1 .
```

**Acceptance:** Build completes without errors. Image runs.

### 2.2 Home Assistant Installation

Install the add-on from the local repository on `192.168.1.44:8123`.

**Acceptance:** Add-on appears in Supervisor → Add-on Store. Installation succeeds.

### 2.3 Home Assistant Startup

Start the add-on and observe logs.

**Acceptance:** 
- Add-on starts without errors
- Encryption key auto-generated (no hardcoded defaults)
- 9 entities per profile published to HA
- Logs show: entities registered, encryption initialized

### 2.4 API Endpoint Validation

```bash
# Through HA Ingress proxy
curl http://192.168.1.44:8123/api/hassio_ingress/<token>/api/v1/fertility/profiles
curl http://192.168.1.44:8123/api/hassio_ingress/<token>/api/v1/fertility/entries
curl http://192.168.1.44:8123/api/hassio_ingress/<token>/docs  # OpenAPI docs
```

**Acceptance:** 
- All endpoints return 200 with valid JSON
- `/docs` renders OpenAPI UI
- Ingress path resolution works (no 404s on nested routes)

### 2.5 Frontend/UI Render

Navigate to the add-on web UI through HA sidebar.

**Acceptance:**
- Dashboard renders with real cycle data
- BBT chart shows actual temperature records
- "Today's Signs" card shows live values
- Profile management works (create, switch, delete)
- Entry form submits and triggers reanalysis
- Toast notifications appear on success/error
- Error boundary catches render failures

### 2.6 Full Test Suite

```bash
# Python tests
cd packages/fertility_engine && pytest
cd packages/data_service && pytest
cd packages/ha_bridge && pytest
cd packages/web_api && pytest

# Frontend tests
cd frontend && npm test
```

**Acceptance:** All 225 tests (160 Python + 65 frontend) pass.

### 2.7 Encryption at Rest

Perform an entry creation and verify database encryption:

```bash
sqlite3 /data/byrd_health.db "SELECT profile_id, substr(temperature, 1, 20) FROM temperature_records LIMIT 1;"
```

**Acceptance:** Temperature values are encrypted blobs, not plaintext floats. Round-trip: create entry → re-read via API → correct temperature returned.

### 2.8 HA Entity Publishing

After startup, check HA Developer Tools → States:

```
sensor.byrd_health_<slug>_today_temp
sensor.byrd_health_<slug>_coverline
sensor.byrd_health_<slug>_ovulation_day
sensor.byrd_health_<slug>_fertility_status
sensor.byrd_health_<slug>_cycle_day
sensor.byrd_health_<slug>_mucus_today
sensor.byrd_health_<slug>_opk_today
sensor.byrd_health_<slug>_next_fertile_start
sensor.byrd_health_<slug>_next_fertile_end
```

Create a new entry and verify entities update.

**Acceptance:** All 9 entities visible. Entities update after entry creation.

---

## 3. Known Non-Blocking Issues

These are known and should NOT block release:

| # | Issue | Severity | Plan |
|---|---|---|---|
| 1 | ADR-0006 violation — `web_api/app.py` imports `HABridge` directly | Low | Quick Win Q1 — implementing HABridgeProtocol in parallel |
| 2 | Mypy path conflict — needs `--explicit-package-bases` | Low | Quick Win Q2 |
| 3 | Frontend chunk size ~700KB | Low | Quick Win Q3 — code splitting |
| 4 | npm audit: 7 vulnerabilities (dev deps only) | Low | Standard React ecosystem noise |

---

## 4. Pass Criteria

All of the following must pass:

- [ ] Docker build succeeds
- [ ] HA install succeeds
- [ ] HA startup succeeds (no errors)
- [ ] API endpoints respond correctly through Ingress
- [ ] Frontend renders through HA Ingress
- [ ] All 225 tests pass
- [ ] Encryption verified (round-trip encrypt/decrypt)
- [ ] All 9 HA entities published and updating

---

## 5. Fail Criteria

If any of the following occur, certification fails:

- Docker build error
- HA install failure
- HA startup crash or hang
- API endpoint returns 500 or timeout
- Frontend white screen or infinite loading
- Any test failure
- Plaintext data in database
- Missing or stale HA entities

---

## 6. Deliverables Expected from Release Engineer

1. **Pass/Fail verdict** — single boolean
2. **Evidence** — logs, screenshots, test output, entity state snapshots
3. **Remediation report** (if FAIL) — failures categorized by severity with proposed fixes
4. **Release confidence score** — high/medium/low with justification

---

## 7. Blocking Note

The Architect will **not** advance to Phase 3 implementation until this validation is complete and receives a PASS verdict.

Quick Wins Q1-Q3 are running in parallel and do not block the release gate.

---

*Handoff prepared by Lead Architect — ready for Release Engineer.*
