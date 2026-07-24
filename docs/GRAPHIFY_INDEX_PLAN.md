# Graphify Index Plan — Byrd Health

> Identifies all entities, services, relationships, and architectural concepts that must be indexed in Graphify.
>
> Graphify is the canonical knowledge layer. Stale state is a project defect.

---

## 1. Indexing Strategy

### 1.1 Node Types

| Node Type | Purpose | Example |
|---|---|---|
| `service` | Deployable service | `fertility-engine`, `ha-bridge` |
| `module` | Code package / library | `algorithms`, `validation` |
| `entity` | Data model / domain object | `Profile`, `Cycle` |
| `agent` | Specialist agent role | `Backend Engineer` |
| `adr` | Architectural decision record | `ADR-001` |
| `api` | API endpoint group | `Fertility API v1` |
| `integration` | External system connection | `Home Assistant`, `ByrdOS` |
| `milestone` | Project phase / milestone | `Phase 0`, `Milestone 1` |
| `document` | Key project document | `LEGACY_REVIEW.md` |
| `concept` | Abstract idea / principle | `Privacy-first`, `Modular Design` |

### 1.2 Relationship Types

| Relationship | Direction | Meaning |
|---|---|---|
| `DEPENDS_ON` | A → B | A requires B to function |
| `IMPLEMENTS` | A → B | A implements interface/contract B |
| `PRODUCES` | A → B | A generates/produces B |
| `CONSUMES` | A → B | A reads/uses B |
| `OWNS` | A → B | A has authority over B |
| `REFERENCES` | A → B | A documents or refers to B |
| `PRECEDES` | A → B | A must happen before B |
| `VERSION_OF` | A → B | A is a new version of B |
| `DEPLOYS_TO` | A → B | A is deployed on B |
| `INTEGRATES_WITH` | A → B | A connects to external system B |
| `HANDLES` | A → B | A processes/manages B |
| `ISOLATES` | A → B | A encapsulates B-specific logic |

---

## 2. Domain Entities

### 2.1 Core Data Entities

These map to database tables and Pydantic models:

| Entity | Type | Description | Legacy Source |
|---|---|---|---|
| `Profile` | entity | User profile with settings | `profiles` table |
| `Cycle` | entity | A single menstrual cycle | `cycles` table |
| `TemperatureRecord` | entity | A BBT reading for a date | `temperatures` table |
| `FertilitySigns` | entity | Daily fertility observations | `fertility_signs` table |
| `Symptom` | entity | Symptom for a date | `symptoms` table |
| `ComputedInsights` | entity | Cached analysis results | `computed_insights` table |
| `DeviceReading` | entity | Raw reading from a device | NEW |

**Relationships:**
- `Profile` → `HAS_MANY` → `Cycle`
- `Cycle` → `HAS_MANY` → `TemperatureRecord`
- `Cycle` → `HAS_MANY` → `FertilitySigns`
- `Cycle` → `HAS_MANY` → `Symptom`
- `Cycle` → `HAS_ONE` → `ComputedInsights`
- `Profile` → `OWNS` → `DeviceReading`

### 2.2 Enum / Value Entities

These are the allowed values for various fields:

| Entity | Type | Values |
|---|---|---|
| `FlowValue` | entity | none, spotting, light, medium, heavy |
| `MucusValue` | entity | dry, sticky, creamy, watery, egg_white |
| `OPKValue` | entity | not_tested, negative, low, high, peak |
| `PositionValue` | entity | low, mid, high |
| `FirmnessValue` | entity | firm, medium, soft |
| `OpeningValue` | entity | closed, medium, open |
| `SymptomType` | entity | cramps, bloating, breast_tenderness, ovulation_pain, headache, spotting, mood_changes, fatigue, other |
| `InterpretationMethod` | entity | standard, conservative |
| `TempUnit` | entity | F, C |
| `CyclePhase` | entity | menstruation, pre_ovulatory, fertile, ovulation, luteal, unknown |

---

## 3. Services

### 3.1 Core Services

| Service | Type | Description |
|---|---|---|
| `fertility-engine` | service | Pure algorithm package. Coverline, ovulation detection, fertile window, cycle analysis, prediction |
| `data-service` | service | Database access layer. CRUD, schema management, encryption, data export/import |
| `web-api` | service | FastAPI REST + WebSocket gateway. Routes, auth, request validation |
| `web-frontend` | service | React SPA. Dashboard, entry forms, charts, history views |
| `ha-bridge` | service | Home Assistant integration bridge. Entity publishing, sensor polling, Lovelace card, Ingress |
| `device-adapters` | service | Device integration adapters. HA sensor, ESPHome, Bluetooth, manual |

### 3.2 Service Dependencies

```
web-frontend ──CONSUMES──► web-api
web-api ───────DEPENDS_ON──► data-service
web-api ───────DEPENDS_ON──► fertility-engine
ha-bridge ────DEPENDS_ON──► web-api
ha-bridge ────INTEGRATES_WITH──► home-assistant
device-adapters ──PRODUCES──► DeviceReading
device-adapters ──CONSUMES──► data-service
web-api ───────DEPLOYS_TO──► ha-addon-container
web-api ───────DEPLOYS_TO──► byrdos-platform (future)
```

### 3.3 Service Isolation Notes

- `ha-bridge` ISOLATES all Home Assistant logic
- `fertility-engine` has zero external dependencies
- `data-service` is engine-agnostic (SQLite or PostgreSQL)
- No service imports from `ha-bridge` except the startup orchestrator

---

## 4. Agent Hierarchy

### 4.1 Specialist Agents

These are the agents that operate on the Byrd Health project:

| Agent | Type | Responsibilities |
|---|---|---|
| `Architect` | agent | System design, ADRs, planning, coordination, approval |
| `Backend Engineer` | agent | FastAPI, services, API design, async tasks |
| `Frontend Engineer` | agent | React SPA, charts, forms, accessibility |
| `Home Assistant Engineer` | agent | HA Bridge, entities, Lovelace card, add-on packaging |
| `Database Engineer` | agent | SQLAlchemy models, Alembic migrations, query optimization |
| `AI/Data Science Engineer` | agent | Fertility algorithms, predictions, statistics |
| `Security Engineer` | agent | Threat modeling, auth, encryption, privacy review |
| `QA Engineer` | agent | Testing (unit, integration, e2e), coverage |
| `DevOps Engineer` | agent | Docker, CI/CD, releases, deployment |
| `Documentation Engineer` | agent | Docs, ADRs, API docs, README maintenance |
| `Knowledge Engineer` | agent | Graphify ownership, knowledge indexing, deduplication |

### 4.2 Agent Relationships

| Agent | Related To | Relationship |
|---|---|---|
| `Architect` | All agents | OWNS coordination |
| `Knowledge Engineer` | Graphify | OWNS knowledge layer |
| `Backend Engineer` | `fertility-engine`, `data-service`, `web-api` | IMPLEMENTS |
| `Frontend Engineer` | `web-frontend` | IMPLEMENTS |
| `Home Assistant Engineer` | `ha-bridge`, `home-assistant` | IMPLEMENTS |
| `Database Engineer` | `data-service` schema | OWNS |
| `AI/Data Science Engineer` | `fertility-engine` algorithms | OWNS |
| `Security Engineer` | All services | REVIEWS |
| `QA Engineer` | All services | TESTS |

---

## 5. Key Documents

These documents should be indexed for cross-referencing:

| Document | Type | Path |
|---|---|---|
| Project Plan | document | `PROJECTPLAN.md` |
| Agent Instructions | document | `AGENTS.md` |
| Architect Prompt | document | `.opencode/agents/architect.md` |
| Legacy Review | document | `docs/LEGACY_REVIEW.md` |
| Migration Plan | document | `docs/MIGRATION_PLAN.md` |
| Architecture Recommendations | document | `docs/ARCHITECTURE_RECOMMENDATIONS.md` |
| Graphify Index Plan | document | `docs/GRAPHIFY_INDEX_PLAN.md` |
| Legacy README | document | `legacy/README.md` |
| Legacy Roadmap | document | `legacy/ROADMAP.md` |

**Document relationships:**
- `docs/LEGACY_REVIEW.md` → REFERENCES → `legacy/app/app.py`
- `docs/MIGRATION_PLAN.md` → REFERENCES → `docs/LEGACY_REVIEW.md`
- `docs/ARCHITECTURE_RECOMMENDATIONS.md` → REFERENCES → `docs/LEGACY_REVIEW.md`
- `docs/GRAPHIFY_INDEX_PLAN.md` → REFERENCES → all documents and entities above

---

## 6. Architectural Decisions (ADRs)

### 6.1 ADRs to Create

| ADR | Title | References |
|---|---|---|
| `ADR-001` | Use FastAPI as web framework | `docs/ARCHITECTURE_RECOMMENDATIONS.md §3.1` |
| `ADR-002` | Use SQLAlchemy + Alembic for data layer | `docs/ARCHITECTURE_RECOMMENDATIONS.md §5.1` |
| `ADR-003` | Isolate HA integration in HA Bridge service | `docs/ARCHITECTURE_RECOMMENDATIONS.md §6.1` |
| `ADR-004` | Use React + TypeScript for frontend | `docs/ARCHITECTURE_RECOMMENDATIONS.md §4.1` |
| `ADR-005` | Use Lit for Lovelace card | `docs/ARCHITECTURE_RECOMMENDATIONS.md §4.3` |
| `ADR-006` | Data encryption at rest strategy | `docs/ARCHITECTURE_RECOMMENDATIONS.md §5.3` |
| `ADR-007` | API versioning strategy | `docs/ARCHITECTURE_RECOMMENDATIONS.md §7.1` |
| `ADR-008` | Database engine portability | `docs/ARCHITECTURE_RECOMMENDATIONS.md §5.2` |
| `ADR-009` | Authentication and authorization | `docs/ARCHITECTURE_RECOMMENDATIONS.md §12.2` |
| `ADR-010` | Device integration adapter pattern | `docs/ARCHITECTURE_RECOMMENDATIONS.md §8.1` |

### 6.2 ADR Lifecycle

| State | Meaning |
|---|---|
| `proposed` | Draft created, awaiting review |
| `accepted` | Approved by Architect and user |
| `superseded` | Replaced by newer ADR |
| `deprecated` | No longer applicable |

---

## 7. API Endpoint Groups

| API Group | Type | Description | Version |
|---|---|---|---|
| `Fertility Entries API` | api | Temperature and sign logging | v1 |
| `Fertility Cycles API` | api | Cycle management and history | v1 |
| `Fertility Profiles API` | api | Profile CRUD | v1 |
| `Fertility Insights API` | api | Analysis results | v1 |
| `Fertility Export API` | api | Data portability | v1 |
| `Fertility WebSocket API` | api | Real-time updates | v1 |
| `Health Check API` | api | Service health | v1 |

**API relationships:**
- All APIs → `IMPLEMENTS` → `web-api` service
- All APIs → `CONSUMES` → `data-service`
- `Fertility Insights API` → `CONSUMES` → `fertility-engine`
- `Fertility WebSocket API` → `CONSUMES` → `ha-bridge` (for HA state changes)

---

## 8. External Integrations

| Integration | Type | Description | Current Status |
|---|---|---|---|
| `home-assistant` | integration | HA Supervisor, entities, Ingress, Lovelace | Active (legacy) |
| `byrdos` | integration | Future deployment platform | Planned |
| `apple-health` | integration | Apple Health data import | Future (Phase 3) |
| `google-health-connect` | integration | Android health data import | Future (Phase 3) |
| `esphome` | integration | Custom ESP32 BBT thermometer | Future (Phase 3) |

**Integration relationships:**
- `ha-bridge` → `INTEGRATES_WITH` → `home-assistant`
- `device-adapters` → `INTEGRATES_WITH` → `esphome` (future)
- `data-service` → `INTEGRATES_WITH` → `apple-health` (future)
- All integrations → `ISOLATED` from core business logic

---

## 9. Legacy System Mapping

For knowledge continuity, map legacy components to new architecture:

| Legacy Component | Maps To | Relationship |
|---|---|---|
| `app/algorithms/coverline.py` | `fertility-engine` module | VERSION_OF |
| `app/algorithms/ovulation.py` | `fertility-engine` module | VERSION_OF |
| `app/algorithms/fertile_window.py` | `fertility-engine` module | VERSION_OF |
| `app/algorithms/cycle_analysis.py` | `fertility-engine` module (split: analysis + orchestration) | VERSION_OF |
| `app/db.py` | `data-service` | VERSION_OF |
| `app/app.py` (routes) | `web-api` | VERSION_OF |
| `app/app.py` (background tasks) | `web-api` task subsystem | VERSION_OF |
| `app/ha_client.py` | `ha-bridge` | VERSION_OF |
| `app/validation.py` | Pydantic models in `web-api` | VERSION_OF |
| `app/templates/` | `web-frontend` React components | VERSION_OF |
| `app/static/js/chart-init.js` | `web-frontend` chart components | VERSION_OF |
| `app/static/js/bbt-card.js` | `ha-bridge` Lit component | VERSION_OF |
| `app/static/css/app.css` | `web-frontend` Tailwind config | VERSION_OF |
| `config.yaml` | `ha-bridge` add-on config | REFINED_VERSION |
| `Dockerfile` | DevOps-owned container build | REFINED_VERSION |

---

## 10. Concepts and Principles

These abstract concepts should be indexed as they guide all decisions:

| Concept | Type | Description |
|---|---|---|
| `Privacy-first` | concept | Local processing, no cloud dependencies, data ownership |
| `Modular Design` | concept | Replaceable services, clear boundaries |
| `AI-first Development` | concept | Delegate to specialized agents, minimize context |
| `Graphify-canonical` | concept | Graphify is the source of truth for project knowledge |
| `Token Optimization` | concept | Minimize context, prefer Graphify references |
| `ByrdOS Compatibility` | concept | Independent now, compatible later via stable APIs |
| `Portable Data` | concept | Open formats, documented schemas, escape hatches |
| `Explainable Intelligence` | concept | Every insight traceable to data and rules |
| `Sympto-thermal Method` | concept | The fertility tracking methodology |

---

## 11. Project Milestones

| Milestone | Type | Description | Status |
|---|---|---|---|
| `Phase 0` | milestone | Discovery & Architecture | In Progress |
| `Phase 1` | milestone | Platform Foundation | Planned |
| `Phase 2` | milestone | Fertility Service MVP | Planned |
| `Phase 3` | milestone | Device Integration | Planned |
| `Phase 4` | milestone | Health Platform Expansion | Planned |

From legacy ROADMAP:
| `Milestone 0` | milestone | Project baseline (completed in legacy) | Complete |
| `Milestone 1` | milestone | Trust, privacy, data safety | Partially Complete |
| `Milestone 2` | milestone | Correct & explainable interpretation | Not Started |
| `Milestone 3` | milestone | HA-native experience | Not Started |
| `Milestone 4` | milestone | Daily logging & chart usability | Not Started |
| `Milestone 5` | milestone | Insights & optional expansion | Not Started |

Legacy milestones provide a feature roadmap that should be addressed within Byrd Health Phases 2-4.

---

## 12. Immediate Graphify Indexing Actions

After Phase 0 documents are reviewed and approved, the Knowledge Engineer should:

1. **Create nodes** for all entities in Section 2
2. **Create nodes** for all services in Section 3
3. **Create nodes** for all agents in Section 4
4. **Create nodes** for all documents in Section 5
5. **Create nodes** for all planned ADRs in Section 6
6. **Create nodes** for all API groups in Section 7
7. **Create nodes** for all integrations in Section 8
8. **Create relationships** as specified in each section
9. **Create legacy-to-new mappings** from Section 9
10. **Create concept nodes** from Section 10
11. **Create milestone nodes** from Section 11
12. **Link milestones** to the ADRs they depend on
13. **Link documents** to the domains they describe
14. **Verify** no duplicate nodes exist
15. **Validate** that all relationships are bidirectional where appropriate

---

## 13. Graphify Health Checks

The Knowledge Engineer should periodically verify:

- [ ] Every service has an OWNS relationship to at least one module
- [ ] Every entity is produced or consumed by at least one service
- [ ] Every ADR references at least one service or concept
- [ ] Every document is referenced by at least one node
- [ ] No orphan nodes exist (no relationships)
- [ ] No circular DEPENDS_ON relationships
- [ ] Legacy components have VERSION_OF links to new components
- [ ] Agent OWNERSHIP covers every service
