# Future Module Strategy

> **Date:** 2026-07-26 | **Architecture:** ADR-0001  
> **Principle:** Modular monolith — new modules extend the platform without creating microservices

---

## Module Template

Every new health module follows this pattern, proven by the fertility module:

```
packages/{module}_engine/             # Pure algorithms, zero framework deps
    pyproject.toml                    # Only pydantic dependency
    src/{module}_engine/
        __init__.py
        models.py                     # Pydantic models for algorithm I/O
        calculator.py                 # Core computation
        analyzer.py                   # Orchestration

packages/{module}_data/               # Optional — extend data_service or standalone
    pyproject.toml
    src/{module}_data/
        __init__.py
        models.py                     # SQLAlchemy models (if new tables)
        repositories.py               # CRUD operations

web_api/routers/{module}.py           # REST endpoints
web_api/schemas/{module}_responses.py # Response models (re-export from data layer)

frontend/src/pages/{Module}/          # UI components
    {Module}Dashboard.tsx
    {Module}Entry.tsx
    {Module}Chart.tsx
    {Module}Settings.tsx
```

---

## Phase 4A: Pregnancy Tracking

**Extension of fertility module — NOT a new module.**

Pregnancy tracking is logically an extension of the fertility cycle model. When a positive pregnancy test is recorded or ovulation+implantation is confirmed, the cycle transitions to a pregnancy.

**Minimal data model addition:**
```python
# Extends Cycle model
class Pregnancy(Base):
    id: UUID
    cycle_id: FK(Cycle)  # The conception cycle
    due_date: date
    current_week: int
    trimester: int
    symptoms: relationship(PregnancySymptom)
```

**Algorithm:** Date math — due date = ovulation_date + 266 days. Current week = (today - LMP) / 7. Trimester = week / 13.

**Work estimate:** 1-2 weeks. 80% reuse of existing fertility infrastructure.

---

## Phase 4B: Symptoms Catalog & Medication Tracking

**New `symptom_catalog` data table.** Currently symptoms are free-text. A catalog enables structured tracking and AI-powered insights.

```python
class SymptomCatalog(Base):
    id: UUID
    name: str           # "Headache", "Cramps", "Bloating"
    category: str       # "pain", "digestive", "mood", "energy", "skin"
    severity_scale: int # 1-3 or 1-5

class Medication(Base):
    id: UUID
    name: str
    dosage: str
    schedule: str       # "daily", "as_needed", "weekly"
    taken_at: datetime
```

**Algorithm:** Correlation analysis between symptoms and cycle phases (AI integration point).

**Work estimate:** 2-3 weeks for catalog + tracking. AI insights deferred to Phase 5A.

---

## Phase 4C: Sleep Tracking

**New `sleep_engine` package.** Sleep data is time-series and benefits from its own engine.

```python
class SleepSession(Base):
    id: UUID
    profile_id: FK(Profile)
    date: date
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    deep_sleep_minutes: int
    rem_sleep_minutes: int
    light_sleep_minutes: int
    awake_minutes: int
    score: int              # 0-100
    source: str             # "manual", "apple_health", "fitbit", "oura"
```

**Algorithm:** Sleep debt calculation. Sleep efficiency scoring. Cycle phase correlation (more REM during luteal?).

**Work estimate:** 3-4 weeks. New engine, new data, new UI.

---

## Phase 4D: Nutrition Tracking

**New `nutrition_engine` package.** Most complex module due to food database requirements.

```python
class FoodItem(Base):
    id: UUID
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    serving_size: str

class Meal(Base):
    id: UUID
    profile_id: FK(Profile)
    date: date
    meal_type: str      # "breakfast", "lunch", "dinner", "snack"
    items: relationship(MealItem)
```

**Challenge:** Food database. Options:
1. Bundle a subset of USDA FoodData Central (offline, large)
2. Manual entry only (simple, labor-intensive)
3. Barcode scanning integration (requires camera, mobile)

**Recommendation:** Start with manual entry. Add offline food database in Phase 5.

**Work estimate:** 4-6 weeks for core tracking. Food database: additional 4 weeks.

---

## Phase 5A: Wearable Integration

**New adapters — NOT new modules.** Wearables are data sources that feed existing modules.

```python
# Under device_adapters/adapters/
wearable_apple_health.py    # HealthKit API → read temperature, sleep, heart rate
wearable_google_fit.py      # Google Fit API → read temperature, sleep, heart rate
wearable_garmin.py          # Garmin Connect API → read sleep, HRV, stress
wearable_fitbit.py          # Fitbit Web API → read sleep, heart rate, temperature
wearable_oura.py            # Oura Cloud API → read temperature, sleep, HRV, readiness
```

**Pattern:** Each adapter implements `DeviceAdapter` Protocol. Reads from cloud API → maps to internal data models → persists via data_service.

**Architecture impact:** Minimal. Adapters are self-contained. Each requires OAuth credentials management (new concern — Phase 5B).

**Work estimate:** 2-3 weeks per adapter. iOS/Android companion app for HealthKit/Google Fit OAuth required for initial pairing.

---

## Phase 5B: AI Integration

**New `ai_engine` package.** Implements ADR-0007 Layer 2 (model engine).

```python
class PredictionModel(Protocol):
    """ADR-0007: Model engine protocol."""
    def predict_ovulation(self, temps: list[float], signs: list[FertilitySigns]) -> date | None: ...
    def predict_fertile_window(self, profile_id: UUID) -> tuple[date, date] | None: ...
    def confidence(self, prediction_type: str) -> float: ...

class AIInsights(Base):
    id: UUID
    profile_id: FK(Profile)
    insight_type: str       # "symptom_correlation", "anomaly", "prediction"
    insight_data: JSON
    confidence: float
    generated_at: datetime
```

**Features (in order):**
1. Template-based cycle explanation (Phase 4B)
2. Bayesian ovulation prediction confidence (Phase 5A)
3. Symptom-phase correlation (Phase 5A)
4. Temperature anomaly detection (Phase 5A)
5. Natural language logging (ByrdOS phase)

**Work estimate:** Dependent on model complexity. Template-based: 1 week. Bayesian: 2-3 weeks. NLP: 4+ weeks (requires LLM integration).

---

## ByrdOS Migration

**Not a new module — a deployment target.** The architecture was designed for this.

| Component | Action |
|---|---|
| HA Bridge | Replace with `ByrdOSBridge` implementing `HABridgeProtocol` |
| Auth | Replace HA Ingress with OAuth2/JWT |
| WebSocket | Replace in-memory broker with Redis Pub/Sub |
| Database | Switch SQLite → PostgreSQL |
| Multi-user | Add `user_accounts` table, scope profiles |

**Work estimate:** TBD — depends on ByrdOS service bus maturity.

---

## When to Split the Monolith

**Current:** Modular monolith. All packages in one repo. Shared CI, shared tests, shared Graphify.

**Split when:** Any of these thresholds are crossed:
1. More than 5 health modules (currently 1)
2. CI runtime exceeds 15 minutes (currently ~8s)
3. Multiple teams contributing to different modules simultaneously
4. Any module requires a different Python version or incompatible dependency

**Recommendation:** Stay monolithic through Phase 4. Re-evaluate at Phase 5.

---

## Module Dependency Rules

New modules must follow these rules, established by the existing architecture:

1. **Engine packages** depend only on `pydantic`. Zero framework or database dependencies.
2. **Data packages** depend only on `sqlalchemy`, `alembic`, and their corresponding engine package (for types).
3. **Router files** go in `web_api/routers/`. One file per module.
4. **Schema files** go in `data_service/schemas/`. Web API re-exports, does not redefine.
5. **Frontend pages** are route-based lazy loaded. One directory per module.
6. **No module depends on another module's engine or data package** unless explicitly declared and reviewed.
7. **Cross-module data sharing** (e.g., sleep quality affects fertility) goes through `data_service`, not direct imports.
