# Dependency Audit

## Python Runtime Dependencies

| Package | Declared In | Status |
|---------|-------------|--------|
| `python-multipart` | `web_api` | **UNUSED** — never imported |
| `pydantic` | `ha_bridge` | **UNUSED** — never imported |

*(Full Python dependency inventory available in package pyproject.toml files.)*

## Node Dependencies

All declared dependencies are used. Caret ranges (`^`) allow minor bumps — acceptable for dev deps, review for production.

## Docker Dependencies

| Issue | Severity |
|-------|----------|
| **Unpinned base image:** `FROM ghcr.io/home-assistant/base:latest` | **CRITICAL** |
| `nodejs`/`npm` unversioned | HIGH |
| DevDeps leak into production image (`testing-library`, `vitest`, `typescript`, `jsdom`) | HIGH |
| No `.dockerignore` | MEDIUM |

## GitHub Actions

`@v4`/`@v5` of standard actions — pinned acceptably.

## Pre-commit

All hooks pinned, consistent versions.

## Vulnerability Concerns

- `cryptography>=42.0` — known CVEs below 43.x; should bump to `>=44.0`

## Missing

- No Python lock file (`pip-compile`)
- No `npm audit` in CI
- No `pip-audit` in CI

## Recommended Actions

1. Pin Docker base image to a digest
2. Remove `python-multipart` from web_api dependencies
3. Bump `cryptography` to `>=44.0`
4. Use `npm install --production` in Docker build
5. Add Python lock file via `pip-compile`
