# Test Audit

## Overview

- **37 test files** across 8 locations
- **~3500 lines** of test code
- **Overall grade: B** — Good, with significant cleanup needed

## Tests to Remove (7)

| Test | Reason |
|------|--------|
| `test_regression.py` | 100% duplicate of existing tests |
| `legacy/tests/test_routes.py` | Obsolete Flask routes |
| `legacy/tests/test_algorithms.py` | Superseded by current test suite |
| `test_protocol.py` | Tests `isinstance` — not app logic |
| `Skeleton.test.tsx` | Only tests CSS classes |
| `test_migrations.py` | Tests structural existence Alembic enforces |
| `validate-vs1.ts` | Superseded by `validate-vs2.ts` |

## Low-Value Tests to Fix (6)

| Test | Issue |
|------|-------|
| `test_full_pipeline_conservative_method` | Only asserts `engine_version` |
| `test_register_adds_adapter` | `assert True` — always passes |
| `test_request_returns_json_on_success` | Zero assertions |
| `test_bridge_start_polling_adds_sensor` | Never asserts anything |
| `C10` in `validate-vs2.ts` | Manual test that always passes |
| `TestMessageProtocol` wrapper | Unit tests for `make_message` via WebSocket infra unnecessarily |

## Fixture Duplication

- 3 different `MockHAClient` implementations
- 2 `_temperature()` helper functions
- 2 broker fixtures
- 2 `MockAdapter` classes

## Coverage Gaps

No tests for:
- Error handling in API
- WebSocket authentication
- Profile switching edge cases
- Encryption
- Health check endpoint
- Concurrent access
- Data validation edge cases
- Cycle transitions
- Migration roundtrips
- Performance/stress
- Frontend error states
- Accessibility beyond `PhaseBanner`

## Inconsistent Patterns

- Sync `TestClient` vs `httpx.AsyncClient`
- `asyncio.run()` inside sync tests
- Mixed class-based vs function-based test organization
