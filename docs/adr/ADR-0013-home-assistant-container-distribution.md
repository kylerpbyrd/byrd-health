# ADR-0013: Home Assistant Add-on Container Distribution

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-26                                     |
| **Deciders** | Lead Architect, User                           |
| **Approved** | 2026-07-26                                     |
| **Amended**  | 2026-07-26 — Dockerfile deprecation not deletion; execution order specified |
| **Replaces** | None (new decision)                            |
| **Scope**    | Home Assistant add-on distribution architecture |
| **Depends**  | ADR-0006 (HA Integration Boundary)             |

---

## 1. Problem

### 1.1 Current Failure

The Home Assistant Supervisor install attempt fails with:

```
COPY packages/ /app/packages/
ERROR: "/packages": not found

COPY frontend/ /app/frontend/
ERROR: "/frontend": not found
```

**Root cause:** HA Supervisor sets the Docker build context to the add-on directory:

```
repository/byrd_health_fertility/   ← build context (3 files)
```

The Dockerfile at that location contains `COPY packages/` and `COPY frontend/` commands. These directories do not exist within the add-on directory context. Docker's security model prohibits COPY paths that traverse above the build context (e.g., `../../packages/`).

### 1.2 Structural Mismatch

Byrd Health is a monorepo application:

```
byrd-health/                    ← repo root
├── packages/                   ← Python packages
│   ├── fertility_engine/
│   ├── data_service/
│   ├── ha_bridge/
│   ├── device_adapters/
│   └── web_api/
├── frontend/                   ← React SPA
├── Dockerfile                  ← works from repo root context
├── run.sh                      ← entrypoint
└── repository/
    ├── repository.yaml         ← HA repository metadata
    └── byrd_health_fertility/  ← HA add-on directory (3 files)
        ├── config.yaml
        └── icon.png
```

HA Supervisor requires the add-on to be self-contained in its directory. The application source spans 5 Python packages + a frontend build — far too large to duplicate into the add-on directory.

### 1.3 Why Other Solutions Don't Work

| Solution | Why It Fails |
|----------|--------------|
| `COPY ../../packages/` in Dockerfile | Docker rejects paths outside build context |
| Move all source into add-on directory | Duplicates the entire codebase; maintenance nightmare |
| Make repo root the add-on directory | HA requires add-ons in subdirectories of the repository |
| Git submodules for add-on | HA Supervisor doesn't resolve submodules during build |
| Local build staging script | Requires user to run a script before HA install; fragile |

---

## 2. Decision

**Byrd Health Fertility will distribute as a pre-built OCI container image published to GitHub Container Registry (GHCR).**

The Home Assistant add-on directory becomes a deployment wrapper — it contains only the metadata HA Supervisor needs to pull and run the pre-built image. No Dockerfile, no source code, no build step in the add-on directory.

### 2.1 Target Architecture

```
Developer push → GitHub Actions → docker build → GHCR (ghcr.io/kylerpbyrd/byrd-health-fertility)
                                                          ↓
Home Assistant Supervisor ← pulls image ← repository/byrd_health_fertility/config.yaml
                                                          ↓
                                                 Container runs /run.sh
```

### 2.2 Container Image

| Property | Value |
|----------|-------|
| Registry | GitHub Container Registry |
| Image | `ghcr.io/kylerpbyrd/byrd-health-fertility` |
| Tags | `2.0.0`, `2.0.0-rc1`, `latest` |
| Base | `ghcr.io/home-assistant/base:latest` |
| Entrypoint | `/run.sh` (bashio-based) |
| Port | 8000 (Ingress) |

### 2.3 Add-on Directory (after migration)

```
repository/
├── repository.yaml                 ← unchanged
└── byrd_health_fertility/
    ├── config.yaml                 ← updated: references image, no build
    ├── run.sh                      ← unchanged (runs inside the container)
    ├── icon.png                    ← add-on store icon
    └── translations/               ← future: i18n
```

No Dockerfile. No source code. The add-on directory is a deployment descriptor only.

### 2.4 config.yaml Changes

**Before (source-build):**
```yaml
# HA Supervisor builds Dockerfile from this directory
# No `image:` key — build from source
```

**After (image-based):**
```yaml
image: ghcr.io/kylerpbyrd/byrd-health-fertility:2.0.0
# HA Supervisor pulls this image; no local build
```

All other config.yaml fields (options, schema, ingress, arch declarations) remain unchanged.

---

## 3. Alternatives Considered

### 3.1 Current Source-Build Model (Rejected)

The Dockerfile in the add-on directory attempts to COPY from the repo root. This fails because HA Supervisor's build context is the add-on directory, not the repo root.

**Rejected because:** Docker security model prohibits it. No workaround exists.

### 3.2 Local Build Context Staging (Rejected)

A script copies source files (packages/, frontend/) into the add-on directory before HA Supervisor builds. The copied files are gitignored.

**Rejected because:**
- User must remember to run the script before every install/update
- Adds ~50MB of duplicated files to the working tree
- Script is platform-specific (PowerShell vs bash)
- Doesn't work for direct GitHub URL repository adds (HA clones fresh)

### 3.3 Split Repository (Rejected)

Maintain a separate repository containing only the add-on files with a Dockerfile that clones the main repo during build.

**Rejected because:**
- Doubles repository maintenance
- Build-time git clone is slow and fragile
- Version synchronization between repos
- No CI benefit over image-based distribution

### 3.4 OCI Image Distribution (Selected)

Pre-build the container image via CI/CD. Publish to GHCR. HA Supervisor pulls and runs the image.

**Selected because:**
- Works with HA Supervisor's add-on model (supports `image:` key)
- Single source of truth (one repo, one build pipeline)
- Reproducible builds via GitHub Actions
- Multi-architecture support via `docker buildx`
- Enables version pinning, rollbacks, and canary deployments
- Standard pattern used by ESPHome, Node-RED, and other complex HA add-ons
- ByrdOS future: same image can be deployed outside HA

---

## 4. Consequences

### 4.1 Positive

| Consequence | Impact |
|-------------|--------|
| Production-ready distribution | Immutable, versioned, signed container images |
| Clean HA integration | Add-on directory is metadata-only; no source build |
| Reproducible builds | CI/CD builds the same image every time from tag |
| Multi-architecture | `docker buildx` supports amd64 + aarch64 in one pipeline |
| Version management | Explicit tags enable rollback and canary testing |
| ByrdOS readiness | Same container image deploys to HA or standalone |
| Reduced HA Supervisor load | No build step; Supervisor just pulls and runs |
| Developer experience | `docker build -t byrd-health:rc1 .` still works locally |

### 4.2 Negative

| Consequence | Mitigation |
|-------------|------------|
| Requires GHCR publishing workflow | GitHub Actions workflow; one-time setup |
| Requires image lifecycle management | Tag strategy documented; old tags retained |
| Local development path changes | Keep root Dockerfile for local `docker build` |
| Image pull on first install | GHCR is fast; images are ~200-400MB |
| CI/CD dependency for releases | Acceptable tradeoff for reproducibility |

### 4.3 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GHCR outage during install | Low | High (can't install) | Users can pre-pull image; local registry fallback |
| Image tag mismatch between config.yaml and published image | Low | High (install fails) | CI validates tag exists before updating config.yaml |
| Base image deprecation | Low | Medium | Pin base image digest in Dockerfile |
| Build breakage on main blocks releases | Medium | Medium | CI runs on PRs; only tag-triggered builds push to GHCR |

---

## 5. Migration from Current RC1

### 5.1 User Data Preservation

| Concern | Answer |
|---------|--------|
| Existing installations | Users must reinstall from the new add-on source |
| Database preservation | `/data/byrd_health.db` persists in HA's add-on data volume — not affected by image change |
| Encryption key preservation | `/data/.byrd_key` persists in data volume — not affected |
| Configuration preservation | `config.yaml` options unchanged — user configs carry forward |
| Rollback path | Revert config.yaml to source-build version; rebuild locally |

### 5.2 Migration Steps for Existing RC1 Users

1. Stop the current add-on
2. Update add-on repository source (if using GitHub URL, just refresh)
3. Reinstall — HA Supervisor pulls the pre-built image instead of building
4. Start — data, keys, and configs are preserved via `/data` volume

---

## 6. References

- `ADR-0006` — Home Assistant Integration Boundary
- `ADR-0001` — Platform Architecture
- `docs/plans/ADDON_CONTAINER_MIGRATION_PLAN.md` — Implementation plan
- `docs/releases/VS1_HANDOFF.md` — VS-1 runtime validation handoff
- Root `Dockerfile` — Container build definition (unchanged)
- `run.sh` — Container entrypoint (unchanged)

---

*Proposed by Lead Architect. Approved 2026-07-26. Implementation delegated per ADDON_CONTAINER_MIGRATION_PLAN.md.*
