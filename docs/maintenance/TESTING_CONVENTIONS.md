# Testing Conventions

## Test organization

- One `tests/` directory per package (e.g. `packages/fertility_engine/tests/`).
- Use `conftest.py` for shared fixtures within each package.
- Test files are named `test_<module>.py` mirroring the source module under test.

## Async patterns

- Use `pytest-asyncio` with `asyncio_mode = "auto"` configured in `pyproject.toml`.
- All async tests should use `async def` — never call `asyncio.run()` inside a sync test.
- The event loop is managed by pytest-asyncio automatically.

## HTTP testing

- Use `httpx.AsyncClient` for API tests (e.g. Lifespan ASGI transport).
- Do not use `starlette.testclient.TestClient` — it is deprecated.

## Fixtures

- Define fixtures in `conftest.py` at the package level.
- Do not duplicate `MockHAClient` — use the shared fixture from `packages/ha_bridge/tests/conftest.py`.
- Fixtures should be stateless where possible to avoid test coupling.

## Assertions

- Every test must have at least one meaningful assertion.
- No `assert True` — such tests provide zero behavioral value.
- Prefer specific assertions (e.g. `assert result == expected` over `assert result`).

## Frontend tests

- Use `vitest` and `@testing-library/react` for component tests.
- One test file per component, located in `frontend/src/__tests__/`.
- Test behavior (rendering, user interaction, state changes), not CSS classes.
- Avoid snapshots for complex UI — they are brittle and low-signal.

## Validation tools

- `tools/validate-vs*.ts` are Playwright E2E tests for live Home Assistant instances.
- These are not run in CI. They require a running HA instance with ingress configured.
- Set `BYRD_HA_URL`, `BYRD_HA_TOKEN`, `BYRD_INGRESS_URL`, and `BYRD_INGRESS_COOKIE` env vars to run.
- MANUAL-only tests that cannot be automated should use `test.skip()`.

## Running tests

| Target     | Command                          |
| ---------- | -------------------------------- |
| Python     | `python -m pytest packages/`     |
| Frontend   | `npm test` (from `frontend/`)    |
| E2E        | `npx playwright test` (optional) |

Python test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`.
