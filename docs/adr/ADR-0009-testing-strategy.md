# ADR-0009: Testing Strategy

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | All code in Byrd Health platform               |

---

## 1. Context

Byrd Health processes health data where algorithmic correctness directly impacts user decisions. Testing must verify:

- Algorithmic correctness (ovulation detection, fertile window)
- Data integrity (CRUD operations, constraints)
- API behavior (status codes, response shapes, error handling)
- UI rendering (component states, form validation)
- Edge cases (missing data, irregular cycles, boundary temperatures)

The legacy application has 11 tests — insufficient coverage for a health application.

## 2. Decision

Adopt a **layered testing strategy** with coverage targets enforced in CI.

### 2.1 Test Layers

| Layer              | Tool                          | Scope                          | Target Coverage |
|--------------------|-------------------------------|--------------------------------|-----------------|
| Unit — Algorithms  | pytest                        | Pure functions in fertility_engine | 95%+           |
| Unit — Services    | pytest + pytest-asyncio       | Data Service, utility functions   | 85%+           |
| Integration — API  | pytest + httpx.AsyncClient    | FastAPI endpoints with test DB    | 80%+           |
| Integration — DB   | pytest + test SQLite          | SQLAlchemy models, migrations     | 85%+           |
| E2E — Frontend     | Vitest + React Testing Library| Component rendering, user flows   | 70%+           |
| Contract — HA      | pytest + mock HA API          | HA Bridge publishes correct entities | 80%+    |
| Property-based     | Hypothesis                   | Algorithm invariants               | Selected tests |

### 2.2 Test Fixture Strategy

```python
# Shared fixtures — isolated, reusable, composable

@pytest.fixture
def temp_db() -> AsyncGenerator[AsyncSession, None]:
    """In-memory SQLite database for testing."""
    ...

@pytest.fixture
def test_profile(temp_db) -> Profile:
    """A default test profile with known settings."""
    ...

@pytest.fixture
def sample_cycle(temp_db, test_profile) -> Cycle:
    """A cycle with 30 days of synthetic temperature data."""
    ...

@pytest.fixture
def api_client(temp_db) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client pointed at test FastAPI app."""
    ...
```

### 2.3 Algorithm Test Patterns

```python
# 1. Known-input tests — specific scenarios with expected outcomes
def test_standard_three_day_shift_confirms_ovulation(): ...

# 2. Edge case tests — boundary conditions
def test_ovulation_not_detected_with_insufficient_temps(): ...

# 3. Regression tests — bugs found and fixed
def test_discarded_temps_do_not_count_toward_shift(): ...

# 4. Property-based tests — invariants that always hold
@given(synthetic_cycle_data())
def test_coverline_never_exceeds_max_temp(data): ...

# 5. Legacy compatibility tests — same inputs → same outputs
def test_matches_legacy_ovulation_detection(): ...
```

### 2.4 API Test Patterns

```python
async def test_create_entry_returns_201(api_client, sample_cycle):
    response = await api_client.post("/api/v1/fertility/entries", json={...})
    assert response.status_code == 201

async def test_entry_with_invalid_temp_returns_422(api_client):
    response = await api_client.post("/api/v1/fertility/entries", json={
        "temp_value": 150.0  # Out of range
    })
    assert response.status_code == 422

async def test_cannot_access_other_profile_data(api_client, profile_a, profile_b):
    # Create data for profile_a, attempt access as profile_b
    ...
    assert response.status_code == 404
```

### 2.5 Frontend Test Patterns

```typescript
// Component rendering test
test("PhaseBanner displays correct phase and cycle day", () => {
  render(<PhaseBanner phase="fertile" cycleDay={14} />);
  expect(screen.getByText("Fertile Window")).toBeInTheDocument();
  expect(screen.getByText("14")).toBeInTheDocument();
});

// Form validation test
test("EntryForm shows error for invalid temperature", async () => {
  render(<EntryForm />);
  await userEvent.type(screen.getByLabelText(/temperature/i), "150");
  await userEvent.click(screen.getByText(/save/i));
  expect(screen.getByText(/temperature must be between/i)).toBeInTheDocument();
});
```

### 2.6 CI Enforcement

```yaml
# .github/workflows/ci.yml
- name: Unit tests
  run: pytest tests/unit/ --cov=fertility_engine --cov-fail-under=95

- name: Integration tests
  run: pytest tests/integration/ --cov=src/ --cov-fail-under=80

- name: Frontend tests
  run: cd frontend && npx vitest run --coverage

- name: Type check
  run: mypy src/ --strict
```

## 3. Consequences

### Positive
- High confidence in algorithm correctness
- CI-enforced coverage prevents regression
- Test fixtures enable fast, isolated development
- Property-based testing catches edge cases humans miss

### Negative
- Writing comprehensive tests takes significant Phase 1 time
- Coverage targets may slow initial development velocity
- Maintaining test fixtures as schema evolves

### Risks
- Coverage targets could encourage low-quality tests — mitigated by code review
- E2E tests may be flaky — mitigated by limiting E2E scope to critical user flows
- Synthetic data may not represent real-world patterns — mitigated by including real-world anonymized test cases

## 4. Phase 1 Testing Scope

| What Gets Tested              | What Does NOT Get Tested (yet)    |
|-------------------------------|-----------------------------------|
| All algorithm functions       | HA Bridge (Phase 2)               |
| All API endpoints             | Lovelace card (Phase 3)           |
| All SQLAlchemy models         | Device adapters (Phase 3)         |
| All Pydantic schemas          | End-to-end HA deployment (Phase 2)|
| Core React components         | Performance benchmarks (Phase 2+) |
| Migration up/downgrade        | Security penetration testing      |

## 5. References

- `docs/LEGACY_REVIEW.md §9.8` — Limited test coverage in legacy
- `docs/MIGRATION_PLAN.md §2.9` — Test suite migration decision
- `ADR-0001` — Platform architecture
- `ADR-0007` — AI/prediction architecture (algorithm tests)
