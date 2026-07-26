# Legacy Application Review — BBT Fertility Tracker

> Version: 1.0.4 | Repository: `kylerpbyrd/bbt-fertility-tracker` | Date of review: 2026-07-23

---

## 1. Executive Summary

The legacy application is a **production-grade, privacy-first Home Assistant Add-on** that tracks basal body temperature (BBT) to monitor menstrual cycles, detect ovulation, and identify fertile windows using the sympto-thermal method. It is feature-complete for a single-user/multi-profile scenario and has been shipped as a real Home Assistant add-on.

**Overall assessment:** A solid foundation. The algorithmic core is well-implemented and tested. The primary architectural limitation is its **monolithic Flask design**, which tightly couples the web UI, business logic, HA integration, and data layer into a single process.

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Runtime | Python | 3.11 |
| Web framework | Flask | 3.0.3 |
| Database | SQLite (WAL mode) | Built-in |
| ORM | None (raw SQL via `sqlite3`) | — |
| Charting | Chart.js + chartjs-plugin-annotation | 4.4.3 / 3.0.1 |
| Frontend | Jinja2 templates + vanilla JS | — |
| Container | Docker (HA `base` image) | — |
| HA Integration | Supervisor REST API (`http://supervisor/core/api`) | — |
| CI/CD | GitHub Actions | — |
| Linting | Flake8 | 7.1.1 |
| Testing | Pytest | 8.3.5 |

---

## 3. Application Structure

```
legacy/
├── app/
│   ├── app.py                    # Flask app (994 lines) — monolithic entry point
│   ├── db.py                     # SQLite schema, connection, migrations (212 lines)
│   ├── ha_client.py              # HA REST API client (306 lines)
│   ├── validation.py             # Input validators (74 lines)
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── coverline.py          # Coverline calculation (55 lines)
│   │   ├── ovulation.py          # Ovulation detection — 3-day shift, conservative, witch's hat (194 lines)
│   │   ├── fertile_window.py     # Fertile window + cycle phase logic (145 lines)
│   │   └── cycle_analysis.py     # Orchestrator: wires algorithms + persists insights (254 lines)
│   ├── templates/                # 7 Jinja2 HTML templates
│   ├── static/
│   │   ├── css/app.css           # Full custom CSS (419 lines)
│   │   ├── js/chart-init.js      # Chart.js initialization (284 lines)
│   │   └── js/bbt-card.js        # Custom Lovelace card (305 lines)
│   └── requirements.txt          # flask==3.0.3 (single dependency)
├── tests/
│   ├── test_routes.py            # 7 route tests (114 lines)
│   └── test_algorithms.py        # 4 algorithm tests (62 lines)
├── Dockerfile                    # HA base image build
├── config.yaml                   # HA add-on metadata
├── run.sh                        # bashio launcher
├── .github/workflows/ci.yml      # CI: test, lint, YAML validate, Docker build
├── repository.yaml               # HA add-on repository metadata
├── pytest.ini / requirements-dev.txt
└── docs/ (release-checklist, data-backup)
```

---

## 4. Existing Features

### 4.1 Fertility Tracking

| Feature | Implementation | Quality |
|---|---|---|
| BBT temperature logging | Manual entry + auto-polling from HA sensor | Good |
| Menstrual flow tracking | spotting/light/medium/heavy | Good |
| Cervical mucus tracking | dry/sticky/creamy/watery/egg_white | Good |
| Cervical position | low/mid/high + firmness + opening | Good |
| OPK (ovulation predictor kit) | not_tested/negative/low/high/peak | Good |
| Symptom tracking | 9 symptom types with severity (1-3) | Good |
| Discarded readings | Flag + reason | Good |
| Notes | Separate temp and signs notes | Good |

### 4.2 Algorithm Features

| Feature | Algorithm | Status |
|---|---|---|
| Coverline | Highest of 6 pre-shift temps + 0.1°F / 0.05°C threshold | Implemented |
| Ovulation — Standard | 3 consecutive temps above coverline | Implemented |
| Ovulation — Conservative | Standard + 3rd temp ≥ 0.2°F / 0.1°C above coverline | Implemented |
| Ovulation — Witch's Hat | Dip on day 2 allowed if days 1,3,4 above | Implemented |
| Fertile Window Start | Calendar rule (shortest cycle − 18) with mucus override | Implemented |
| Fertile Window End | 3 days after temp shift (confirmed) or ovulation + 2 days (possible) | Implemented |
| Cycle Phase Detection | menstruation → pre_ovulatory → fertile → ovulation → luteal | Implemented |
| Pregnancy Indicator | ≥ 18 consecutive elevated post-ovulatory temps | Implemented |
| Short Luteal Warning | Luteal phase < 10 days | Implemented |
| Period Prediction | Ovulation + avg luteal (or cycle start + avg cycle) | Implemented |

### 4.3 Home Assistant Integration

| Feature | Details |
|---|---|
| HA Entity Publishing | 9 entities per profile (sensor.* and binary_sensor.*) |
| Entity naming | `bbt_{slug}_{metric}` pattern |
| HA Sensor Polling | Configurable interval (1-60 min) |
| Auto-import | Polls HA sensor entities, auto-logs temperatures |
| Lovelace Card | Custom `bbt-fertility-card` web component |
| Ingress support | Ingress path middleware for HA sidebar integration |

### 4.4 User Features

| Feature | Details |
|---|---|
| Multi-profile | Track multiple people in one add-on |
| Data Export | JSON export of all profile data |
| °F/°C support | Configurable per profile |
| Interpretation method | Standard vs. Conservative per profile |
| CSRF protection | HTML form token verification |
| BBT Chart | Full annotated Chart.js with coverline, fertile box, ovulation line, discarded indicators, mucus/OPK dots |
| Dashboard | Phase banner, stat tiles, mini chart, warnings |
| Cycle History | Table of past cycles with insights |
| Cycle Detail | Full chart + daily log table |
| Mobile-responsive | CSS grid breakpoints for small screens |

---

## 5. Database Design

**Engine:** SQLite with WAL journal mode, `check_same_thread=False`  
**Location:** `/data/bbt.db`  
**Schema version:** 1 (forward-only migration framework present)

### 5.1 Tables

| Table | Purpose | Key Columns |
|---|---|---|
| `profiles` | User profiles (multi-user) | name, slug, temp_unit, interpretation_method, ha_sensor_entity, active |
| `cycles` | Menstrual cycles per profile | profile_id (FK), start_date, end_date, cycle_length |
| `temperatures` | BBT readings per cycle | cycle_id (FK), date, temp_value, time_taken, is_discarded, discard_reason |
| `fertility_signs` | Daily fertility observations | cycle_id (FK), date, menstrual_flow, cervical_mucus, cervical_position, cervical_firmness, cervical_opening, opk_result |
| `symptoms` | Per-day symptom records | cycle_id (FK), date, symptom_type, severity |
| `computed_insights` | Cached analysis results | cycle_id (FK, UNIQUE), coverline, ovulation_date, ovulation_confirmed, fertile_start/end, luteal_length, pregnancy_indicator |
| `settings` | Key-value profile settings | profile_id (FK), key, value |
| `schema_migrations` | Migration tracking | version, applied_at |

### 5.2 Design Observations

- **Good:** Foreign keys with CASCADE deletes, UNIQUE constraints on natural keys, WAL mode for concurrent reads, row factories for dict-like access
- **Concern:** No encryption at rest for sensitive health data
- **Concern:** Single-file SQLite — backup reliance on Home Assistant backup system
- **Concern:** No proper ORM — raw SQL strings throughout, vulnerable to refactoring errors
- **Concern:** Schema version is `1` but the migration framework only has a placeholder — no real migrations exist yet

---

## 6. Business Logic Architecture

### 6.1 Algorithm Pipeline

```
Temperatures + Signs
        │
        ▼
  detect_ovulation()       ← ovulation.py
        │                    (coverline → shift detection → confidence)
        ▼
  compute_fertile_window()  ← fertile_window.py
        │                    (calendar rule + mucus rule → window boundaries)
        ▼
  analyze_cycle()           ← cycle_analysis.py (orchestrator)
        │                    (luteal length, pregnancy indicator, short luteal)
        ▼
  computed_insights table   ← persisted results
        │
        ▼
  HA entity publish         ← ha_client.py
```

### 6.2 Separation of Concerns (Current State)

| Layer | Where it lives | Coupling |
|---|---|---|
| Web routing | `app.py` | Tightly coupled to db.py and algorithms |
| Data access | `db.py` | Raw SQL, shared connection in Flask `g` |
| Validation | `validation.py` | Pure functions — **well-separated** |
| Algorithms | `algorithms/` package | Pure functions, no Flask dependency — **well-separated** |
| HA Integration | `ha_client.py` | HTTP calls only, no Flask dependency — **well-separated** |
| Background analysis | `app.py` (`_async_analyze_and_publish`) | Thread-based, couples algorithms + db + HA |
| HA sensor polling | `app.py` (`_poll_ha_sensors`) | Timer-based, couples db + HA client |

---

## 7. User Workflows

### 7.1 Daily Logging

1. User opens Dashboard → sees current phase, cycle day, chart
2. If HA sensor configured, sees live reading chip
3. Clicks "Log Today" → Entry page
4. Enters temperature (optionally pre-filled from HA sensor), time, signs, symptoms
5. If period start checkbox checked → closes current cycle, starts new one
6. Submit → saves to DB → triggers async analysis → publishes HA entities

### 7.2 Dashboard Viewing

1. Loads current cycle phase banner, stats tiles, mini chart
2. Displays any warnings (short luteal, pregnancy indicator)
3. Shows today's logged signs summary

### 7.3 History Review

1. History page → table of all cycles with ovulation, luteal, length
2. Click cycle → detail page with full Chart.js graph + daily log table

### 7.4 Profile Management

1. Profiles page → create, activate, delete profiles
2. Settings page → temp unit, interpretation method, HA sensor entity

---

## 8. Strengths

1. **Algorithmic correctness:** The sympto-thermal method implementation is well-researched and tested. The three variants (standard, conservative, witch's hat) are properly handled.

2. **Privacy-first design:** All data is local. No cloud dependencies for core functionality. The product guardrails in the ROADMAP.md explicitly prohibit data sharing.

3. **Clean algorithm separation:** The `algorithms/` package has zero Flask or HA dependencies. Pure functions with typed inputs/outputs. This is the most architecturally sound part of the codebase.

4. **HA integration depth:** Entity publishing, sensor polling, Lovelace card, Ingress support — the integration is comprehensive for a v1 product.

5. **Multi-profile support:** Already handles the complexity of multiple users within a single add-on, with proper profile-scoped data access.

6. **Validation layer:** Dedicated `validation.py` with typed validation functions, enum values, and time/date range checks.

7. **Documentation quality:** README, ROADMAP, release checklist, data backup docs are thorough. The roadmap shows thoughtful prioritization (trust/reliability before features).

8. **CI pipeline:** Tests, linting, YAML validation, and Docker build — all automated in GitHub Actions.

9. **Data portability:** JSON export exists. The format is versioned (`"format": "bbt-fertility-tracker-export", "version": 1`).

10. **Chart.js with annotations:** The chart implementation (coverline annotation, fertile window box, ovulation line, discarded points, mucus/OPK dots via custom plugin) is sophisticated for a self-hosted tool.

---

## 9. Weaknesses

1. **Monolithic architecture:** `app.py` is 994 lines mixing routing, business logic, background tasks, and startup. Not modular.

2. **Flask is synchronous:** Every request blocks. Background analysis uses `threading.Thread` with daemon threads — no task queue, no retry logic, no error recovery.

3. **No API versioning:** The `/api/` endpoints have no version prefix. Changes will break HA automations.

4. **SQLite limitations:** While adequate for a single add-on, SQLite in WAL mode has limited concurrent write support. The `check_same_thread=False` pattern is a workaround for Flask's threading, not a proper async solution.

5. **Tight coupling in routes:** Route handlers directly call `get_db()`, execute raw SQL, and call algorithms inline. No service layer abstraction.

6. **Temperature unit conversion is blocked:** The settings page explicitly prevents changing °F/°C after data exists — this is listed as a known issue in the ROADMAP.

7. **No authentication beyond HA Ingress:** The app relies entirely on HA's Ingress proxy for access control. There is no internal auth mechanism.

8. **Minimal test coverage:** Only 11 tests total (7 routes, 4 algorithms). No tests for edge cases in ovulation detection, fertile window calculation, or HA client.

9. **CDN dependency (mitigated but not eliminated):** Chart.js is bundled in the Docker image at build time, but the approach (wget in Dockerfile) means the image is tied to specific versions hardcoded in the Dockerfile.

10. **No WebSocket support:** HA entities are updated via REST polling only. Real-time updates would require WebSocket integration.

11. **Flask development server in production:** The app runs with `app.run(host="0.0.0.0", port=8099)`, which is the Flask development server — not production-grade.

12. **No structured logging:** Uses Python's `logging` module with basic config. No log levels per module, no structured log format, no log rotation.

---

## 10. Technical Debt

| Item | Severity | Effort to Fix |
|---|---|---|
| Monolithic Flask app | High | Major refactor |
| Raw SQL throughout | Medium | Replace with ORM |
| No async support | High | Switch to FastAPI/async |
| Dev server in production | High | Use uvicorn/gunicorn |
| No API versioning | Medium | Add `/api/v1/` prefix |
| Temperature unit conversion blocked | Medium | Implement conversion logic |
| Minimal test coverage | High | Write comprehensive test suite |
| No error retry/monitoring | Medium | Add task queue, health checks |
| Hardcoded versions in Dockerfile | Low | Use build args or package management |
| Schema migration framework is placeholder | Medium | Implement real Alembic migrations |
| Thread-based background tasks | Medium | Replace with proper async task queue |

---

## 11. Security Concerns

| Concern | Risk Level | Mitigation in Legacy |
|---|---|---|
| Health data stored in plaintext SQLite | High | None — relies on filesystem security |
| No API authentication | High | Relies on HA Ingress proxy only |
| CSRF protection | Medium | Present for HTML forms, absent for JSON API |
| No audit logging | Medium | No record of who accessed what data |
| No encryption at rest | High | None |
| Secret key stored as file | Low | `/data/secret_key` — acceptable for HA add-on context |
| SUPERVISOR_TOKEN used for HA API | Low | Standard HA pattern, container-scoped |
| No rate limiting | Low | Single-user context mitigates this |
| No input sanitization beyond validation | Low | SQLite with parameterized queries prevents injection |

---

## 12. Scalability Concerns

| Concern | Current Limit | Future Impact |
|---|---|---|
| Single-process Flask | ~10 concurrent users max | ByrdOS multi-user will require async |
| SQLite write contention | 1 concurrent writer | Acceptable for single-user, not for multi-user |
| In-memory state (g object) | Per-request scoped | Not a problem for Flask, but pattern doesn't scale to async |
| No caching layer | Every request hits DB | Acceptable for <1000 records, will degrade |
| Background tasks in threads | No queue, no retry | Lost analysis if thread crashes |
| HA entity publishing | Synchronous HTTP per entity | ~9 HTTP calls per analysis — acceptable at low scale |
| Chart.js rendering | Client-side only | Acceptable — no server rendering needed |

---

## 13. Key Files Reference

| File | Lines | Role |
|---|---|---|
| `app/app.py` | 994 | Main Flask application |
| `app/db.py` | 212 | Database schema, connection, migration framework |
| `app/ha_client.py` | 306 | HA REST API client |
| `app/validation.py` | 74 | Input validators |
| `app/algorithms/coverline.py` | 55 | Coverline calculation |
| `app/algorithms/ovulation.py` | 194 | Ovulation detection (3 variants) |
| `app/algorithms/fertile_window.py` | 145 | Fertile window + cycle phase |
| `app/algorithms/cycle_analysis.py` | 254 | Analysis orchestrator |
| `app/static/js/chart-init.js` | 284 | Chart.js initialization |
| `app/static/js/bbt-card.js` | 305 | Custom Lovelace web component |
| `app/static/css/app.css` | 419 | Application styles |
| `app/templates/dashboard.html` | 176 | Dashboard template |
| `app/templates/entry.html` | 208 | Entry form template |
| `tests/test_routes.py` | 114 | Route tests |
| `tests/test_algorithms.py` | 62 | Algorithm tests |
