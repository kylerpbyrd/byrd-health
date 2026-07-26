# Add-on Container Migration Plan

> **ADR:** ADR-0013 — OCI Container Image Distribution
> **Status:** Approved — execution in progress
> **Date:** 2026-07-26
> **Amendments:** Dockerfile deprecated not deleted; execution order: DevOps → Backend → HA → QA

---

## Executive Summary

Migrate the Home Assistant add-on from source-build (HA Supervisor builds Dockerfile from add-on directory) to image-based distribution (HA Supervisor pulls pre-built image from GHCR). This resolves the build context failure and establishes a production-grade distribution pipeline.

---

## Phase 1 — Repository Structure Changes

### 1.1 Current State

```
repository/
├── repository.yaml
└── byrd_health_fertility/
    ├── config.yaml
    ├── Dockerfile         ← DELETE: source-build no longer used
    └── ... (minimal files)
```

### 1.2 Target State

```
repository/
├── repository.yaml                      ← unchanged
└── byrd_health_fertility/
    ├── config.yaml                      ← MODIFY: add image: key
    ├── run.sh                           ← unchanged (runs inside container)
    └── icon.png                         ← unchanged
```

### 1.3 config.yaml Changes

**Add `image:` key:**
```yaml
image: ghcr.io/kylerpbyrd/byrd-health-fertility:2.0.0
```

**Remove:** nothing. All other keys (options, schema, ingress, arch, startup, boot, homeassistant_api, map, init) remain unchanged.

**Validate:** HA Supervisor recognizes `image:` key and skips the local Docker build step.

### 1.4 Files to Deprecate

| File | Action |
|------|--------|
| `repository/byrd_health_fertility/Dockerfile` | **DEPRECATE** — renamed to `Dockerfile.deprecated` or marked with a deprecation notice. NOT deleted until GHCR migration validated. Preserves rollback capability. |

### 1.5 Files to Update

| File | Change |
|------|--------|
| `repository/byrd_health_fertility/config.yaml` | Add `image:` key |
| `tools/stage-local.ps1` | Update to reflect image-based workflow; optionally repurpose as a local build + tag helper |

### 1.6 Files NOT Changed

| File | Why |
|------|-----|
| Root `Dockerfile` | Still used for local dev builds and CI pipeline |
| Root `config.yaml` | Redundant with add-on directory copy; kept for local dev reference |
| `run.sh` | Entrypoint inside the container; identical for local and image builds |
| `packages/` | Application source; unchanged |
| `frontend/` | Application source; unchanged |

---

## Phase 2 — Container Image Specification

### 2.1 Image Name

```
ghcr.io/kylerpbyrd/byrd-health-fertility
```

### 2.2 Version Strategy

| Tag | Purpose | Trigger |
|-----|---------|---------|
| `2.0.0-rc1` | Current release candidate | Manual workflow dispatch |
| `2.0.0` | Production release | Git tag `v2.0.0` |
| `latest` | Latest production release | Git tag matching `v*` |
| `dev` | Development/nightly | Push to `main` branch |
| `pr-{number}` | PR validation | Pull request opened |

### 2.3 Base Image

```dockerfile
FROM ghcr.io/home-assistant/base:latest@sha256:<digest>
```

Pin to a specific digest for reproducible builds. Update digest periodically.

### 2.4 Labels

```dockerfile
LABEL \
  io.hass.version="2.0.0" \
  io.hass.type="addon" \
  io.hass.arch="aarch64|amd64"
```

### 2.5 Image Size Target

| Layer | Approximate Size |
|-------|-----------------|
| Base (HA Alpine) | ~50MB |
| Python + venv | ~80MB |
| Node + npm | ~40MB |
| Package installs | ~30MB |
| Frontend build output | ~500KB |
| Total | ~200MB |

---

## Phase 3 — GitHub Actions CI/CD Pipeline

### 3.1 Workflow File

Create: `.github/workflows/container-build.yml`

### 3.2 Workflow Triggers

```yaml
on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      tag:
        description: 'Image tag'
        required: true
        default: 'dev'
```

### 3.3 Workflow Jobs

#### Job 1: Test (always runs)

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Python tests
      run: pip install -e ".[dev]" && pytest
    - name: Frontend tests
      run: cd frontend && npm ci && npm test
```

#### Job 2: Build and Push (on push to main, tags, and workflow_dispatch)

```yaml
build:
  needs: test
  runs-on: ubuntu-latest
  permissions:
    contents: read
    packages: write
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Docker metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/kylerpbyrd/byrd-health-fertility
        tags: |
          type=ref,event=tag
          type=ref,event=branch
          type=sha,prefix=pr-
          type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### 3.4 Build Cache Strategy

Use GitHub Actions cache (`type=gha`) for Docker layer caching. Invalidated when Dockerfile or package dependencies change. Reduces build time from ~10 min to ~2 min for cache hits.

---

## Phase 4 — Multi-Architecture Support

### 4.1 Target Architectures

| Architecture | HA Platform | Priority |
|-------------|-------------|----------|
| `linux/amd64` | Generic x86-64, Intel NUC, Proxmox VM | P0 (primary) |
| `linux/aarch64` | Raspberry Pi 4/5, ARM64 SBC | P1 (required for Community Store) |
| `linux/armv7` | Raspberry Pi 3, older ARM | P2 (nice to have) |

### 4.2 Build Matrix

```yaml
- name: Build and push (multi-arch)
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    platforms: linux/amd64,linux/aarch64
    tags: ${{ steps.meta.outputs.tags }}
```

### 4.3 Architecture Validation

| Check | Method |
|-------|--------|
| amd64 image runs | CI job on ubuntu-latest runner |
| aarch64 image runs | QEMU emulation in CI, or manual RPi test |
| armv7 image runs | Manual test on RPi 3 hardware |

### 4.4 Known ARM Limitations

- `nodejs` and `npm` packages in Alpine ARM may have different versions
- `cryptography` wheel compilation requires `cargo`/Rust on ARM
- Python 3.12+ ARM wheels available via piwheels

---

## Phase 5 — Home Assistant Integration Validation

### 5.1 config.yaml Migration

Compare current vs new:

| Key | Current | New | Reason |
|-----|---------|-----|--------|
| `image` | (absent) | `ghcr.io/kylerpbyrd/byrd-health-fertility:2.0.0` | Tells HA Supervisor to pull, not build |
| All other keys | unchanged | unchanged | Options, schema, ingress, arch preserved |

### 5.2 Validation Checklist

| # | Check | Method | Critical? |
|---|-------|--------|-----------|
| 1 | HA Supervisor discovers add-on from repository | Add repo URL → add-on appears in store | YES |
| 2 | Add-on installs (image pull) | Click INSTALL → succeeds | YES |
| 3 | Add-on starts | Click START → green Running status | YES |
| 4 | No startup errors in logs | Log tab shows clean startup | YES |
| 5 | Encryption key auto-generated | Check `/data/.byrd_key` exists | YES |
| 6 | Database migrations run | Log shows "Database migrations applied" | YES |
| 7 | UI renders through Ingress | OPEN WEB UI → dashboard loads | YES |
| 8 | All 7 frontend pages load | Navigate each nav item | YES |
| 9 | API endpoints respond | curl health, profiles, insights | YES |
| 10 | OpenAPI docs render | /docs loads in browser | YES |
| 11 | HA entities published | Developer Tools → States → filter `bbt_` | YES |
| 12 | Entity values correct | cycle_day, phase, etc. show real values | YES |
| 13 | Data persists across restart | Create entry → restart → entry still visible | YES |
| 14 | Upgrade from 2.0.0-rc1 to 2.0.0 | Change tag in config.yaml → reinstall | YES |
| 15 | Config options respected | Change temp_unit in config → reflected in API | YES |

### 5.3 Rollback Procedure

1. Stop the add-on
2. Change `image:` tag back to previous version (e.g., `2.0.0-rc1`)
3. Reinstall add-on
4. Start — data volume preserved

---

## Agent Delegation Plan

### Agent 1: DevOps Engineer

**Responsibilities:**
- Create `.github/workflows/container-build.yml`
- Configure GHCR authentication (GITHUB_TOKEN)
- Set up Docker Buildx for multi-architecture
- Create `docker/metadata-action` tag strategy
- Validate: CI workflow runs successfully on push to main
- Test: Image published to GHCR with correct tags

**Deliverables:**
- `container-build.yml` workflow file
- Successful CI run with image in GHCR
- Screenshot of GHCR package page showing tagged images

**ADR References:** ADR-0013 §3
**Graphify References:** service: ci-cd, integration: github-actions

---

### Agent 2: Home Assistant Engineer

**Responsibilities:**
- Update `repository/byrd_health_fertility/config.yaml` — add `image:` key
- Delete `repository/byrd_health_fertility/Dockerfile` (not needed)
- Validate add-on directory is HA-compatible (only metadata files)
- Test: HA Supervisor discovers and installs the add-on
- Test: Container runs and all 9 entity types publish

**Deliverables:**
- Updated `config.yaml`
- VS-1 validation evidence (screenshots per checklist)
- Entity state verification

**ADR References:** ADR-0013 §2.3, ADR-0006
**Graphify References:** integration: home-assistant, service: ha-bridge

---

### Agent 3: Backend Engineer

**Responsibilities:**
- Validate root `Dockerfile` builds correctly (unchanged, but verify)
- Validate `run.sh` works in the pre-built image context
- Ensure `BYRD_DATABASE_URL`, `BYRD_SECRET_KEY`, and all env vars resolve correctly in the HA Supervisor container environment
- Test: Image starts, API responds, database migrations run, encryption works

**Deliverables:**
- Confirmation that `docker build -t byrd-health:rc1 .` succeeds
- Confirmation that `docker run` with env vars starts correctly
- API health check response

**ADR References:** ADR-0013 §2.2
**Graphify References:** service: web-api, service: data-service

---

### Agent 4: QA Engineer

**Responsibilities:**
- Execute full VS-1 validation checklist against the image-based add-on
- Test fresh install (no prior data)
- Test upgrade from RC1 source-build to image-based (if feasible)
- Test uninstall/reinstall cycle (verify data volume persistence)
- Test config option changes (temp_unit, notification toggles)
- Verify all 327 automated tests still pass

**Deliverables:**
- VS-1 PASS/FAIL verdict per checklist item
- Evidence package (screenshots, logs, API outputs)
- Regression test results

**ADR References:** ADR-0013 §5
**Graphify References:** milestone: vs-1-validation

---

## Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| GHCR image pull fails during HA install | HIGH | LOW | Test pull before committing config.yaml change; provide local build fallback instructions |
| Image tag in config.yaml doesn't exist | HIGH | LOW | CI validates tag exists before config.yaml update is merged |
| Container doesn't start in HA Supervisor env | HIGH | MEDIUM | Test with `docker run -e SUPERVISOR_TOKEN=...` to simulate HA env |
| Data migration from source-build to image-based fails | MEDIUM | LOW | Both use same `/data` volume path; database is SQLite — no migration needed |
| config.yaml `image:` key not recognized by older HA versions | LOW | LOW | `image:` key supported since HA 0.7x (several years); minimum HA version documented |
| Multi-arch build fails on ARM | MEDIUM | MEDIUM | QEMU emulation in CI; manual RPi test before release |

---

## Approval Checkpoint

**APPROVED 2026-07-26** with amendments:
1. Dockerfile deprecated, not deleted (rollback safety)
2. Execution order enforced: DevOps → Backend → HA → QA
3. Version tags: `dev`, `2.0.0-rc1`, `2.0.0`, `latest`
4. Migration path documented (source-build RC1 → image-based RC1 → 2.0.0)

**Execution begins with Phase A (DevOps).**
