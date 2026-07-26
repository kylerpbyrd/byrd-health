Production Readiness Audit — Byrd Health
Executive Summary
Overall repository score: 42/100
Ship recommendation: NOT READY
Area	Score	Readiness
Architecture	52/100	Needs boundary correction
Code quality	54/100	Functional gaps across contracts
Security	38/100	Not safe for standalone exposure
Testing	35/100	Unit-heavy, critical flows unproven
Documentation	46/100	Extensive but contradictory/stale
Home Assistant readiness	25/100	Not a distributable mature HA add-on
Release readiness	22/100	Gates and packaging are not credible
ByrdOS readiness	38/100	Good intentions, but HA coupling leaks inward

The repository has a thoughtful modular direction, a pure-ish fertility engine, TypeScript frontend, async data access, and substantial test scaffolding. However, it is not production-ready as a Home Assistant Community Add-on or as a dependable ByrdOS foundation.
The strongest blocker is that the public add-on repository layout is not installable: [`repository/`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/repository) contains only repository.yaml, while the actual add-on files live at repository root and the required staged repository/byrd_health_fertility/ directory is generated locally and untracked by [`tools/stage-local.ps1`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/tools/stage-local.ps1).
Critical blockers
The repository cannot be consumed as a standard HA add-on repository.
[`repository/repository.yaml`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/repository/repository.yaml) exists, but no committed add-on directory contains config.yaml, Dockerfile, and run.sh. The temporary layout is generated only by [`tools/stage-local.ps1`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/tools/stage-local.ps1).
Priority: Critical

The production database does not use Alembic migrations, and migration 001 disagrees with current models.
Startup invokes Base.metadata.create_all() in [`packages/web_api/src/web_api/app.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/app.py), bypassing Alembic entirely. Meanwhile [`_001_initial_schema.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/migrations/versions/_001_initial_schema.py) declares temperatures.temp_value as Float, while [`models.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/models.py) now stores encrypted text. This makes upgrades and recovery unsafe.
Priority: Critical

The normal frontend entry workflow submits an API-invalid symptom payload.
[`EntryForm.tsx`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/components/EntryForm.tsx) sends symptoms: string[]; [`api.ts`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/lib/api.ts) forwards that unchanged; [`entries.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/entries.py) requires list[SymptomItem] objects. Selecting symptoms produces a 422 response.
Priority: Critical

Changing a profile from Fahrenheit to Celsius silently reinterprets historical data rather than converting it.
[`profiles.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/profiles.py) permits changing temp_unit; [`repositories.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/repositories.py) persists no conversion or immutable measurement-unit provenance; [`analysis.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/analysis.py) then analyzes those values under the newly selected unit.
Priority: Critical

The standalone Docker deployment documented by the project is unauthenticated.
[`tools/release.ps1`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/tools/release.ps1) publishes a standalone docker run -p 8000:8000 workflow, while all API routes in [`packages/web_api/src/web_api/routers/`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers) lack authentication and [`config.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/config.py) defaults CORS to ["*"]. Health records can be read, changed, or exported by any reachable caller.
Priority: Critical

No independent runtime evidence supports the claimed release readiness.
[`docs/releases/RELEASE_STATUS.md`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/docs/releases/RELEASE_STATUS.md) correctly says runtime validation is pending, but [`docs/RELEASE_CANDIDATE_VALIDATION.md`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/docs/RELEASE_CANDIDATE_VALIDATION.md) claims a pass based substantially on code audit. This conflicts with [`AGENTS.md`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/AGENTS.md), which requires actual Docker, HA install/startup, UI, API, and runtime validation.
Priority: Critical

Category Findings
Category	Current implementation and strengths	Weaknesses, risks, debt, and required improvement	Priority
Repository structure	Clear top-level packages/, frontend/, docs/, tools/, and graph/. Legacy code is isolated in [`legacy/`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/legacy).	Root add-on files are not in a committed HA repository add-on directory. Generated staging is untracked. Tracked database sidecars are excluded by .gitignore but present in the working tree. Commit a canonical repository/byrd_health_fertility/ layout or make root itself the documented add-on source; remove generation as the release mechanism.	Critical
Package architecture	[`fertility_engine`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/fertility_engine) is cleanly isolated from HA and persistence. data_service centralizes persistence.	ADR-0001 and ADR-0006 promise the web API has no HA dependency, but [`app.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/app.py) imports and constructs HABridge; [`device_adapters/pyproject.toml`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/device_adapters/pyproject.toml) depends on ha-bridge; device adapters import HA client types. Introduce outbound ports in a neutral application layer and make HA composition-only.	High
Home Assistant integration	config.yaml includes ingress, Supervisor API access, options, architecture declarations, and persistent /data. [`run.sh`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/run.sh) uses bashio and a persistent database path.	Entity publishing receives raw CycleInsights from [`web_api/analysis.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/analysis.py), but [`ha_bridge/entities.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/ha_bridge/src/ha_bridge/entities.py) expects dashboard fields such as cycle_day, phase, last_temp, and avg_cycle_length. HA will publish "unknown"/missing values. The client is not closed on shutdown. Profile deletion leaves stale HA states. Notifications can repeat on every analysis and daily reminders are always for slug "default" in [`notifications.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/ha_bridge/src/ha_bridge/notifications.py).	High
Fertility engine	Pure functions in [`fertility_engine`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/fertility_engine) are small and testable. Models express major inputs and outputs.	Core algorithms accept list[dict] internally in [`ovulation.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/fertility_engine/src/fertility_engine/ovulation.py) and [`fertile_window.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/fertility_engine/src/fertility_engine/fertile_window.py), reducing type safety. Explainability is limited to method/confidence; there is no persisted rule trace, source-record set, or calculation provenance. [`web_api/analysis.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/analysis.py) drops ovulation_confidence before persistence. Define typed normalized inputs and a versioned explanation/audit object.	High
API design	Versioned REST paths are consistent under /api/v1/fertility; FastAPI generates OpenAPI; response models are mostly explicit.	Route contracts are inconsistent: [`api.ts`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/lib/api.ts) calls POST /cycles/ with no body, while [`cycles.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/cycles.py) requires start_date; Settings “Start New Cycle” always fails. Domain validation is weak: profile unit/method fields are length-limited strings in [`data_service/schemas.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/schemas.py), not enums. Error response shape is not standardized.	High
Frontend	React Query, route-level lazy loading, error boundary, skeletons, responsive Tailwind layout, and accessible labels exist. [`App.tsx`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/App.tsx) handles ingress basename.	API client contains contract drift. WebSocket typing expects one device reading while [`devices.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/devices.py) broadcasts a map of readings. Calendar quick entry does not invalidate dashboard, history, chart, or today-entry queries. Pages frequently treat network failure as empty data, e.g. [`HistoryPage.tsx`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/pages/HistoryPage.tsx). Add generated client types from OpenAPI and contract tests.	High
Security	AES-GCM with random nonces in [`encryption.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/encryption.py) is a good base. The run script generates a non-hardcoded key. Sensitive values are encrypted in repositories.	No authentication/authorization for standalone use; allow_credentials=True with wildcard CORS is unsafe/misconfigured in [`app.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/app.py). /data/.byrd_key is written without restrictive permissions in [`run.sh`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/run.sh); key rotation, backup/restore, integrity recovery, and threat model are absent. Profile names, dates, cycle metadata, and computed insights remain plaintext. The documented “HKDF-equivalent” claim is inaccurate: key derivation is plain SHA-256 concatenation.	Critical
Performance	SQLite WAL is enabled; frontend chunks are manually split; React routes are lazy-loaded.	Dashboard requires multiple API calls and backend repeats N+1 queries in [`cycles.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/cycles.py) and [`calendar.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/routers/calendar.py). Calendar decrypts all overlapping cycle records before filtering. No indexes beyond uniqueness constraints, load test, latency budget, or database-size plan exists.	Medium
Testing	Broad unit/integration test directories exist across packages; frontend has component tests.	Tests use create_all() rather than migrations, so they do not detect the migration/schema incompatibility. There are no committed HA Supervisor E2E tests, Docker runtime tests, API/frontend contract tests, auth/security tests, browser tests, migration upgrade tests, or device-to-entry persistence tests. The frontend tests mock the failing cycle creation API call.	Critical
Documentation	Documentation volume is strong: user guide, ADRs, release checklists, architecture, onboarding, troubleshooting.	Documentation is internally inconsistent: README says Phase 2 production RC; Git shows Phase 3 work; [`ADR-0011`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/docs/adr/ADR-0011-device-adapter-pattern.md) documents endpoints different from implementation; release documents claim both pass and gated status. [`docs/DEVELOPER_GUIDE.md`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/docs/DEVELOPER_GUIDE.md) says “all three packages,” omitting HA bridge and device adapters. A new engineer would not become reliably productive within an hour.	High
Release engineering	CI has Python, frontend, and Docker jobs. Scripts exist for build, stage, and packaging.	CI runs npx eslint src/ but eslint and a config are absent from [`frontend/package.json`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/package.json); the check is non-reproducible or fails. Docker uses unpinned base:latest, broad Python ranges, and npm install instead of lockfile-enforced npm ci. Docker build runs only on pull requests, not main pushes. No SBOM, image scan, provenance, multi-architecture build, published image, signed release, or enforced release gate.	Critical
Long-term maintainability	Names are generally clear and package code is compact. Architecture ADRs identify desired direction.	Global mutable singletons in [`dependencies.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/dependencies.py), duplicated schemas in data_service and web_api, duplicated ingress middleware in ha_bridge and web_api, static engine_version, and stale Graphify records will compound maintenance. [`graph/index.json`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/graph/index.json) lists nodes that do not exist as files.	High

Architecture assessment
The intended dependency direction is good:
frontend → web_api → fertility_engine + data_service, with HA at the edge.
The actual direction is not clean:
web_api → device_adapters → ha_bridge, plus web_api → ha_bridge directly in lifespan setup.
That violates the explicit ADR-0001/ADR-0006 principle that HA must be removable by replacing only the bridge. A ByrdOS service would currently need to carry HA dependencies or fork application startup.
The package split is useful, but calling every package a “service” overstates the architecture: these are in-process Python libraries without independent deployability, persistence ownership boundaries, or explicit inter-package interfaces. That is acceptable for a single HA container, but should be documented as a modular monolith.
Top 10 strengths
Pure fertility package separation in [`packages/fertility_engine`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/fertility_engine).
Async SQLAlchemy repository pattern in [`packages/data_service`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service).
Strong initial use of Pydantic/FastAPI response models.
API version prefixing under /api/v1/fertility.
React Query and lazy routing in [`frontend/src/App.tsx`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/App.tsx).
Ingress-aware SPA path handling in [`web_api/ingress.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/ingress.py).
Random-nonce AES-GCM implementation.
HA configuration surface is explicit in [`config.yaml`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/config.yaml).
The repository recognizes runtime validation as a release requirement.
ADR coverage is unusually strong for a project of this size.
Top 10 weaknesses
No committed installable HA add-on repository structure.
Migration strategy is declared but not used.
Current migration and ORM schema conflict.
Unauthenticated standalone health-data API.
Frontend/API contract failures in symptoms and new-cycle creation.
Unit changes corrupt semantic interpretation of historical temperature values.
HA entities receive incomplete analysis payloads.
Device, WebSocket, and sensor ingestion are not wired end-to-end.
CI frontend lint job is not provisioned.
Release documentation contains unsupported pass claims and stale findings.
Immediate improvements
Commit a canonical HA repository layout and validate installation from a clean clone. Update [`repository/repository.yaml`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/repository/repository.yaml), add repository/byrd_health_fertility/config.yaml, Dockerfile, and run script—or redesign the project layout so the root is unquestionably the add-on directory.

Replace create_all() in [`app.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/app.py) with an explicit migration command in [`run.sh`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/run.sh). Create encryption-schema migrations and test upgrade from every supported prior version.

Fix frontend contract drift:
transform symptoms to { symptom_type, severity } in [`frontend/src/lib/api.ts`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/lib/api.ts);
require a date for createCycle() and collect it in [`SettingsPage.tsx`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/frontend/src/pages/SettingsPage.tsx);
add OpenAPI-driven contract tests.

Disallow changing temp_unit after data exists until a transactional conversion migration is implemented. Enforce enums in [`data_service/schemas.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/data_service/src/data_service/schemas.py).

Separate HA-only composition from web API startup. [`web_api`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api) should depend on a neutral application port, not concrete HA modules.

Add standalone authentication or remove standalone deployment claims from [`tools/release.ps1`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/tools/release.ps1). Replace permissive CORS with explicitly configured trusted origins.

Make HA entity generation consume a dashboard projection, not bare CycleInsights; fix the producer in [`web_api/analysis.py`](C:/Users/kyler/OneDrive/Documents/Code/projects/byrd-health/packages/web_api/src/web_api/analysis.py).

Pin builds: replace base:latest, broad package constraints, and Docker npm install; use digest-pinned base images and npm ci.

Repair CI by adding ESLint/configuration or removing the invalid job; add coverage thresholds, migration tests, and a release workflow.

Mark all current release claims as pending until clean-clone Docker, HA installation, ingress, UI, entity, notification, device, and shutdown evidence exists.

Long-term improvements
Introduce a neutral domain/application layer with ports for persistence, notifications, device ingestion, and deployment integration.
Treat schema/versioned exports and encryption-key lifecycle as first-class compatibility contracts.
Generate frontend API types from OpenAPI and reject incompatible changes in CI.
Add HA integration tests using a real Supervisor-compatible environment.
Define a realistic ByrdOS migration target: PostgreSQL behavior, identity/auth model, multi-user authorization, event broker, and data migration guarantees.
Make Graphify automatically validated in CI; currently it is aspirational rather than authoritative.
Maintainability forecast
6 months: Manageable for the current author if critical contracts and release mechanics are corrected immediately.
1 year: High risk without migrations, API contract generation, reproducible builds, and removal of HA coupling from core application startup.
3 years: Not maintainable as a health-platform foundation in its current form. The lack of stable persistence evolution, auth model, and clean deployment boundary would force a costly migration or rewrite.
Would I approve the architecture on joining the project? I would approve the direction, not the present implementation. The package boundaries and ADR intent are promising, but the actual dependency graph, persistence lifecycle, release mechanics, and runtime evidence do not meet a production standard.


2:04 PM