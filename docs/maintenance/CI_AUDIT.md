# CI/CD Audit

## Workflow Inventory

| Workflow | Jobs |
|----------|------|
| `ci.yml` | `python-checks`, `frontend-checks`, `docker-build` |
| `container-build.yml` | `test`, `build-and-push` |

## Issues Found (13)

| # | Issue | Severity |
|---|-------|----------|
| 1 | Broken pip install: no `build-system` in root `pyproject.toml` | HIGH |
| 2 | `pytest-cov` installed but `--cov` never used | LOW |
| 3 | Pre-commit stricter than CI: `mypy --strict` locally vs relaxed in CI | MEDIUM |
| 4 | CI doesn't run `ruff format` | MEDIUM |
| 5 | Docker builds only `linux/amd64` (config claims 4 architectures) | HIGH |
| 6 | Redundant test execution across both workflows | MEDIUM |
| 7 | No caching for pip/npm | MEDIUM |
| 8 | `stage-local.ps1` checks wrong directory | LOW |
| 9 | Duplicate `config.yaml` files | LOW |
| 10 | Docker build only on PRs, not on main | MEDIUM |
| 11 | No multi-stage Docker build | MEDIUM |
| 12 | No `HEALTHCHECK`/non-root user in Dockerfile | MEDIUM |
| 13 | `container-build` test job skips linting/typecheck | MEDIUM |

## Gaps (8)

1. No coverage reporting
2. No security/dependency scanning
3. No multi-arch Docker builds
4. No E2E tests in CI
5. No pre-commit enforcement in CI
6. No legacy exclusion boundary test
7. No Python version matrix
8. No release automation

## Pre-commit vs CI Matrix

| Check | Pre-commit | CI |
|-------|------------|-----|
| `ruff` (lint) | Yes | Yes |
| `ruff format` | Yes | **No** |
| `mypy --strict` | Yes | **No** (relaxed) |
| `pytest` | No | Yes |
| Frontend lint (`tsc`, `eslint`) | Yes | Yes |
| Frontend tests (`vitest`) | No | Yes |
