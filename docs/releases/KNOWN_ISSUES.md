# Known Issues — Byrd Health v2.0.0 RC1

> **Owner:** Release Engineer
> **Last Updated:** 2026-07-26

---

## Issue Severity Definitions

| Severity | Meaning |
|----------|---------|
| **BLOCKER** | Must be fixed before production release |
| **HIGH** | Should be fixed before production; may require runtime verification |
| **MEDIUM** | Should be addressed but does not block release |
| **LOW** | Cosmetic or edge-case; can ship as-is |

---

## Active Issues

### KI-001: Settings Page Does Not Persist to Backend

| Field | Value |
|-------|-------|
| **Severity** | **HIGH** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | Backend Engineer + Frontend Engineer |
| **Component** | `frontend/src/pages/SettingsPage.tsx` |
| **Description** | The `handleSave` function sets a local `saved` state but never calls a PATCH API to persist `temp_unit` or `interpretation_method` changes. The settings reset on page reload. The profile update endpoint (`PATCH /api/v1/fertility/profiles/{profile_id}`) exists and accepts `ProfileUpdateSchema`, but the Settings page does not call it. |
| **Impact** | Users who change temperature unit or interpretation method will lose their settings on page reload or navigation. |
| **Reproduction** | 1. Navigate to Settings → 2. Change temperature unit to °C → 3. Click "Save Settings" → 4. Reload page → 5. Setting reverts to °F |
| **Recommended Fix** | Wire `handleSave` to call `updateProfile()` API with current profile ID. Add `useMutation` for profile update. |
| **Priority** | Fix before Beta gate. |

---

### KI-002: Entity Cleanup Not Performed on Profile Deletion

| Field | Value |
|-------|-------|
| **Severity** | **MEDIUM** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/bridge.py` |
| **Description** | When a profile is deleted via the API, there is no mechanism to remove the corresponding HA entities. The 6-9 entities per profile remain as stale entries in Home Assistant's state registry. |
| **Impact** | Stale entities accumulate in HA; users see entities for deleted profiles. |
| **Recommended Fix** | Add `remove_profile_entities()` to HA Bridge. Call it from the profile delete router in `web_api/routers/profiles.py`. |
| **Priority** | Fix before Production gate. |

---

### KI-003: Notification IDs Are Not Per-Profile

| Field | Value |
|-------|-------|
| **Severity** | **MEDIUM** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/notifications.py` |
| **Description** | Notification IDs like `byrd_health_fertile_window` are global strings. If two profiles both trigger the fertile window notification, the second call overwrites the first because HA persistent notifications are keyed by `notification_id`. |
| **Impact** | With multi-profile setups, only one profile's fertile window notification is visible at a time. |
| **Recommended Fix** | Suffix notification IDs with profile slug: `byrd_health_{slug}_fertile_window`. |
| **Priority** | Fix before multi-profile documentation is published. |

---

### KI-004: Publish Methods Are Warning-Only Stubs

| Field | Value |
|-------|-------|
| **Severity** | **LOW** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | Backend Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/bridge.py` |
| **Description** | `publish_entities(profile_slug)` and `publish_all_profiles()` log warnings: "use publish_insights for now" and "publish from lifespan for now". The only working publishing path is `publish_insights()` which requires the full insights dict. |
| **Impact** | If any code path calls these stub methods, entities will not publish. Currently no code paths do — the lifespan and routers all use `publish_insights()`. |
| **Recommended Fix** | Implement or remove. If `publish_insights()` is the canonical API, make the stubs delegate to it, or remove them to prevent misuse. |
| **Priority** | Clean up before Production gate. |

---

### KI-005: No unique_id on HA Entities

| Field | Value |
|-------|-------|
| **Severity** | **LOW** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/entities.py` |
| **Description** | Entities are published to HA via `POST /states/{entity_id}` without a `unique_id` in the payload. This means entities are not registered in HA's entity registry and cannot be managed through the HA UI (Settings → Devices & Services → Entities). They only exist in the state machine. |
| **Impact** | Users cannot customize entity names, icons, or visibility through the HA UI. Entities disappear on HA restart until the add-on republishes them. |
| **Recommended Fix** | Add `unique_id` field to the state POST payload. Use a deterministic ID like `byrd_health_{profile_uuid}_{entity_key}`. |
| **Priority** | Fix before Production gate for polish. |

---

### KI-006: HAClient Timeout Hardcoded at 5 Seconds

| Field | Value |
|-------|-------|
| **Severity** | **LOW** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/client.py` |
| **Description** | The HTTP client timeout is hardcoded as `_DEFAULT_TIMEOUT = 5.0`. This is not configurable. For the HA Supervisor internal network, 5 seconds is amply sufficient, but there is no escape hatch if latency increases. |
| **Impact** | Minimal — supervisor comms are sub-millisecond. |
| **Recommended Fix** | Make timeout configurable via `HABridgeConfig` or environment variable. |
| **Priority** | Nice to have. |

---

### KI-007: npm audit — 7 Vulnerabilities

| Field | Value |
|-------|-------|
| **Severity** | **LOW** |
| **Discovered** | 2026-07-26 — Prior audit |
| **Owner** | Frontend Engineer |
| **Component** | `frontend/package.json` |
| **Description** | `npm audit` reports 7 vulnerabilities in dev dependencies. All are in the React/Vite ecosystem toolchain. None affect production bundles. |
| **Impact** | No runtime impact. Standard React ecosystem noise. |
| **Recommended Fix** | Run `npm audit fix` periodically. |
| **Priority** | Routine maintenance. |

---

### KI-008: Device Adapters Installed But Not Wired Into HA Config

| Field | Value |
|-------|-------|
| **Severity** | **MEDIUM** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `run.sh`, `packages/device_adapters/` |
| **Description** | The device adapter package is installed and the `DeviceRegistry` is created in the app lifespan, but no adapters are registered by default. The `config.yaml` has `ha_sensor_entity` as an option, but there's no `devices` list in the config schema that would allow registering multiple adapters at startup. The Phase 3 plan proposes a `devices:` YAML list but this is not implemented in config.yaml or run.sh. |
| **Impact** | Device adapters exist in code but cannot be configured by users without manual API calls. |
| **Recommended Fix** | Either: (a) wire the single `ha_sensor_entity` option to auto-register an `HASensorAdapter` in the lifespan, or (b) implement the full `devices:` YAML config list from the Phase 3 plan. |
| **Priority** | Fix before Phase 3 completion. |

---

### KI-009: Lovelace Card Hardcodes API Endpoint Path

| Field | Value |
|-------|-------|
| **Severity** | **LOW** |
| **Discovered** | 2026-07-26 — Release Audit |
| **Owner** | HA Engineer |
| **Component** | `packages/ha_bridge/src/ha_bridge/card/ha-card.js` |
| **Description** | The custom Lovelace card computes `API_BASE` from `import.meta.url` by stripping `/ha-card.js`. This assumes the card is served from the same origin as the API. If the card is served from a CDN or different path, API calls will fail. |
| **Impact** | Card only works when served from `/ha-card.js` alongside the API. |
| **Recommended Fix** | Accept `api_base` as a card configuration option, or read from `window.__INGRESS_PATH__`. |
| **Priority** | Fix if CDN deployment is planned. |

---

## Resolved Issues

| # | Issue | Resolution | Date |
|---|-------|------------|------|
| KI-R1 | ADR-0006 violation — direct ha_bridge import | Implemented HABridgeProtocol | 2026-07-25 |
| KI-R2 | Mypy path conflict | Added explicit_package_bases | 2026-07-25 |
| KI-R3 | Frontend chunk size ~700KB | Code splitting implemented | 2026-07-25 |
| KI-R4 | **KI-001** — Settings page doesn't persist | Rewired to use `PATCH /api/v1/fertility/profiles/{id}` | 2026-07-26 |
| KI-R5 | **KI-003** — Notification IDs not per-profile | `byrd_health_{slug}_{suffix}` format; slug-aware methods | 2026-07-26 |
| KI-R6 | **KI-004** — Stub publish methods log warnings | Changed to DEBUG-level; no user-visible warnings | 2026-07-26 |
| KI-R7 | **KI-005** — No unique_id on entities | Added `unique_id` to all 9 entity types | 2026-07-26 |
| KI-R8 | **KI-006** — Hardcoded 5s timeout | Configurable via `HABridgeConfig.ha_api_timeout` | 2026-07-26 |
| KI-R9 | **KI-008** — HA sensor not wired to device adapter | Auto-registers `HASensorAdapter` on startup when configured | 2026-07-26 |

---

## Issue Count by Severity

| Severity | Count |
|----------|-------|
| BLOCKER | 0 |
| HIGH | 0 |
| MEDIUM | 2 (KI-002, KI-008) |
| LOW | 3 (KI-007, KI-009) |

> **Note:** KI-008 was partially resolved (auto-registration in lifespan). The full `devices:` YAML config list from Phase 3 plan remains deferred.

---

*Issues discovered during runtime validation will be appended here with VS- prefix.*
