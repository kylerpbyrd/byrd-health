# ADR-0007: AI/Prediction Architecture

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Fertility algorithms, predictions, future ML   |

---

## 1. Context

The fertility intelligence in Byrd Health relies on the sympto-thermal method — a rules-based algorithm combining temperature patterns (coverline, thermal shift) with fertility signs (cervical mucus, OPK results). The legacy application implements this as a pure-function algorithm package.

Requirements:
- Algorithmic core must be explainable — every insight traceable to data and rules
- Must support standard and conservative interpretation methods
- Must accommodate future machine learning models without rewriting the rules engine
- Must be independently testable with synthetic and real-world data
- Must handle edge cases: missing readings, irregular cycles, discarded data

## 2. Decision

Implement the fertility intelligence as a **pure Python package** (`fertility_engine`) with two layers:

### 2.1 Layer 1: Rules Engine (Phase 1-2)

Classic sympto-thermal method algorithms, ported from the legacy application with type safety and expanded test coverage.

| Module              | Responsibility                                       | Source   |
|---------------------|------------------------------------------------------|----------|
| `coverline`         | Compute coverline from pre-shift temperatures        | Legacy   |
| `ovulation`         | Detect ovulation via 3-day shift rule + variants     | Legacy   |
| `fertile_window`    | Compute fertile window boundaries + cycle phase      | Legacy   |
| `cycle_analysis`    | Orchestrate analysis pipeline → CycleInsights        | Legacy   |
| `prediction`        | Period prediction, cycle length estimation           | Legacy   |

All functions are pure — receive data, return results. No database access, no HTTP calls, no framework dependencies.

### 2.2 Layer 2: Model Engine (Phase 4+)

Future machine learning models that enhance or replace rules with learned patterns.

```python
class PredictionModel(Protocol):
    """Future ML model interface — not implemented in Phase 1-2."""

    def predict_ovulation(self, cycle_data: CycleData) -> OvulationPrediction: ...
    def estimate_fertile_window(self, cycle_data: CycleData) -> FertileWindowEstimate: ...
    def confidence_score(self, prediction: Any) -> float: ...
```

The rules engine remains as the primary system. ML models augment with confidence scores and alternative predictions. Users can compare rule-based vs. model-based insights.

### 2.3 Data Flow

```
Temperature Records + Fertility Signs
                 │
                 ▼
    ┌────────────────────────┐
    │   Fertility Engine      │
    │   ┌──────────────┐     │
    │   │ Rules Engine │     │────► CycleInsights (explainable)
    │   └──────────────┘     │
    │   ┌──────────────┐     │
    │   │ Model Engine │     │────► Predictions (confidence-scored)
    │   │ (future)     │     │
    │   └──────────────┘     │
    └────────────────────────┘
                 │
                 ▼
         ComputedInsights (persisted)
```

### 2.4 Key Design Principles

1. **Explainability over opacity** — Rules engine output includes the data and rule that produced each insight
2. **Deterministic rules** — Same input always produces same output (rules engine only)
3. **Versioned insights** — `engine_version` field in `computed_insights` tracks which algorithm version produced the result
4. **Confidence levels** — Insights carry confidence: `confirmed`, `possible`, `estimated`
5. **Safe defaults** — When data is insufficient, return `None` insights rather than guessing

### 2.5 Input/Output Contracts

```python
# Input: typed records from the data layer
class TemperatureRecord(BaseModel):
    date: date
    temp_value: float
    cycle_day: int
    is_discarded: bool = False

class FertilitySignsRecord(BaseModel):
    date: date
    cervical_mucus: MucusValue | None = None
    opk_result: OPKValue | None = None
    # ... other signs

# Output: typed insights with confidence
class CycleInsights(BaseModel):
    coverline: float | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    ovulation_confidence: Literal["confirmed", "possible", "none"] = "none"
    ovulation_method: str = "none"
    fertile_start_date: date | None = None
    fertile_end_date: date | None = None
    post_ovulatory_infertile_date: date | None = None
    luteal_length: int | None = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    consecutive_elevated_temps: int = 0
    engine_version: str = "1.0.0"
```

## 3. Consequences

### Positive
- Pure functions enable comprehensive unit testing
- No framework coupling means the engine can be used in any Python context
- Version tracking enables re-analysis when algorithms improve
- ML path is designed but not blocking Phase 1-2 delivery

### Negative
- Rules engine is less adaptive than ML models for atypical cycle patterns
- Confidence levels are heuristic, not statistical (for now)
- Separating rules from data access requires more explicit data passing

### Risks
- Algorithm changes could produce different results for same data — mitigated by version tracking and re-analysis triggers
- Edge cases not covered by legacy implementation — mitigated by expanded test suite with synthetic edge-case data

## 4. Implementation Notes

- All algorithms ported from `legacy/app/algorithms/` with type annotations added
- Existing algorithm tests (`legacy/tests/test_algorithms.py`) are preserved and expanded
- New tests cover: missing readings, irregular cycles, boundary temperatures, discarded readings, minimum data thresholds
- The `cycle_analysis.py` orchestrator is split: pure analysis stays in the engine; DB persistence moves to the Data Service

## 5. References

- `docs/LEGACY_REVIEW.md §6` — Business logic architecture analysis
- `docs/LEGACY_REVIEW.md §4.2` — Algorithm feature inventory
- `docs/MIGRATION_PLAN.md §2.1` — Algorithm package migration decision
- `ADR-0001` — Platform architecture
