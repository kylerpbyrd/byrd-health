# Changelog

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
