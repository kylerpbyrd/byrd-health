# Changelog

## v2.1.0 (2026-07-26) — Phase 3: Device Integration & Real-Time

### Added
- **Device Adapter Framework:** Protocol-based `DeviceAdapter` interface with `DeviceRegistry` for pluggable hardware support
- **HA Sensor Adapter:** Wraps existing HA entity polling into the adapter contract
- **ESPHome Adapter:** Native ESPHome device integration via HA REST API
- **Bluetooth Adapter:** BLE GATT thermometer support (IEEE 11073-20601 parsing, bleak-based)
- **WebSocket Real-Time:** In-memory pub/sub broker at `/api/v1/fertility/ws` with `device_reading` and `analysis_complete` message types
- **Live Dashboard:** Real-time updates via WebSocket — dashboard refetches on analysis complete, toast notifications on device readings
- **Entry Form Auto-Fill:** Pre-populates temperature from connected devices with user-edit guard
- **Device Status Indicator:** Live/Offline badge on dashboard showing WebSocket connection state
- **Canonical WebSocket Protocol:** Versioned message envelope (`docs/specs/WEBSOCKET_PROTOCOL.md`) — stable across HA, standalone, and future ByrdOS
- **Device REST API:** `GET /devices`, `POST /devices/read`, `GET /devices/{id}/status`

### Changed
- WebSocket kill switch removed — hook connects by default
- Route-based code splitting for all frontend pages (React.lazy + Suspense)
- Mypy `explicit_package_bases` configured for all sub-packages
- HA Bridge composition root imports documented as accepted exception (ADR-0006)

### Fixed
- ESPHomeAdapter properly exported from adapters package
- Device adapter tests integrated into root pytest (53 tests, 265 total)
- WebSocket contract drift resolved — frontend and backend conform to same protocol

### Known Issues
- **C8 (VS-2):** Dashboard "Live/Offline" indicator shows "Offline" despite WebSocket connecting through Ingress. Direct `page.evaluate` WS test succeeds; React hook's `isConnected` state may not propagate to UI. Under investigation for Phase 4.

---

## v2.0.0 (2026-07-26)

### Added
- Complete rewrite as Home Assistant Add-on
- Privacy-first architecture (all local, encrypted at rest)
- Multi-profile support
- Sympto-thermal method fertility tracking
- BBT chart with coverline, fertile window, and ovulation markers
- Cycle history with phase visualization
- Home Assistant entity publishing (9 entities per profile)
- HA Ingress support with dynamic path resolution
- Data export (JSON)
- Skeleton loaders, toast notifications, error boundaries
- Accessibility improvements (skip-to-content, aria labels)

### Changed
- Migrated from legacy Python/Flask to FastAPI + React + TypeScript
- SQLite database with AES-256-GCM encryption at rest
- Modular architecture (fertility engine, data service, web API, HA bridge)

### Removed
- CDN-hosted Lovelace card (planned for Phase 3)
- Legacy BBT Fertility Tracker codebase
