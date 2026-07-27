# RC1 Runtime Validation Plan — Byrd Health v2.0.0

> **Release Engineer:** Independent certification
> **Date:** 2026-07-26
> **HA Instance:** 192.168.1.44:8123

---

## Executive Summary

RC1 passes all automated checks. **Zero features have been verified at runtime on a live Home Assistant instance.** The code audit confirms all implementations are architecturally sound, but evidence always wins over assumptions.

This plan divides runtime validation into 4 sessions, ordered by dependency. Each session must PASS before the next begins. The Release Engineer will analyze user-provided evidence and issue a PASS/FAIL verdict per session.

---

## Validation Philosophy

1. **Every feature must be exercised at runtime.** Passing tests is not sufficient.
2. **Evidence always wins over implementation.** If a feature behaves differently than expected at runtime, the runtime behavior is the truth.
3. **No assumptions.** If evidence is unavailable, the feature is marked "NOT YET VALIDATED" — never "VERIFIED."
4. **The release gate does not advance until all validation sessions pass.**

---

## Validation Sessions

### Session 1: Startup, Ingress, Core UI, API, Entities
**Goal:** Verify the add-on boots, serves the UI through HA Ingress, exposes the API, and publishes entities.

| Feature | Priority | Status |
|---------|----------|--------|
| Docker rebuild & HA install | CRITICAL | AWAITING EVIDENCE |
| Add-on startup (no errors) | CRITICAL | AWAITING EVIDENCE |
| Encryption key auto-generation | CRITICAL | AWAITING EVIDENCE |
| UI renders through Ingress | CRITICAL | AWAITING EVIDENCE |
| Dashboard loads with data | CRITICAL | AWAITING EVIDENCE |
| All API endpoints respond | HIGH | AWAITING EVIDENCE |
| OpenAPI docs render | HIGH | AWAITING EVIDENCE |
| 6-9 entities per profile published | CRITICAL | AWAITING EVIDENCE |
| All 7 frontend pages load | HIGH | AWAITING EVIDENCE |
| Navigation between pages works | HIGH | AWAITING EVIDENCE |

### Session 2: Data Entry, Charts, Cycle Management
**Goal:** Verify the core fertility tracking workflow functions end-to-end.

| Feature | Priority | Status |
|---------|----------|--------|
| Create profile | CRITICAL | AWAITING EVIDENCE |
| Log a temperature entry | CRITICAL | AWAITING EVIDENCE |
| Log fertility signs | CRITICAL | AWAITING EVIDENCE |
| BBT chart renders with data | CRITICAL | AWAITING EVIDENCE |
| Coverline appears on chart | HIGH | AWAITING EVIDENCE |
| Fertile window shading on chart | HIGH | AWAITING EVIDENCE |
| Cycle detail view | HIGH | AWAITING EVIDENCE |
| Calendar view with data | HIGH | AWAITING EVIDENCE |
| Quick entry from calendar | HIGH | AWAITING EVIDENCE |
| Start new cycle (period start) | HIGH | AWAITING EVIDENCE |
| Data export (JSON) | MEDIUM | AWAITING EVIDENCE |
| Delete profile | MEDIUM | AWAITING EVIDENCE |
| Profile switching (activate) | MEDIUM | AWAITING EVIDENCE |

### Session 3: Notifications, Device Adapters, WebSocket
**Goal:** Verify real-time features, HA integration depth, and device connectivity.

| Feature | Priority | Status |
|---------|----------|--------|
| Fertile window notification | HIGH | AWAITING EVIDENCE |
| Ovulation detected notification | HIGH | AWAITING EVIDENCE |
| Period prediction notification | HIGH | AWAITING EVIDENCE |
| Daily temp reminder notification | HIGH | AWAITING EVIDENCE |
| WebSocket connection from frontend | HIGH | AWAITING EVIDENCE |
| Entity update on entry creation | CRITICAL | AWAITING EVIDENCE |
| Lovelace dashboard card | MEDIUM | AWAITING EVIDENCE |
| HA Sensor adapter (if configured) | MEDIUM | AWAITING EVIDENCE |
| Device reading broadcast via WebSocket | MEDIUM | AWAITING EVIDENCE |

### Session 4: End-to-End Workflow, Edge Cases, Mobile
**Goal:** Validate real-world usage patterns and production readiness.

| Feature | Priority | Status |
|---------|----------|--------|
| Multi-day entry workflow | HIGH | AWAITING EVIDENCE |
| Multiple cycles in history | HIGH | AWAITING EVIDENCE |
| Add-on restart preserves data | CRITICAL | AWAITING EVIDENCE |
| Multi-profile entity isolation | HIGH | AWAITING EVIDENCE |
| Mobile Companion App ingress | MEDIUM | AWAITING EVIDENCE |
| Settings persistence (KI-001) | HIGH | AWAITING EVIDENCE |
| Discarded temperature display | MEDIUM | AWAITING EVIDENCE |
| Error boundary behavior | LOW | AWAITING EVIDENCE |
| Toast notifications (success/error) | LOW | AWAITING EVIDENCE |

---

## Features Not In Scope for RC1 Runtime Validation

These features are implemented in code but will not be validated in RC1 because they depend on external hardware or are Phase 3+ scope:

| Feature | Reason |
|---------|--------|
| Bluetooth thermometer (bleak) | Requires physical BLE thermometer |
| ESPHome native API | Requires ESPHome device on network |
| ByrdOS integration | Phase 4 — not yet implemented |
| Sleep/nutrition modules | Phase 4 — not yet implemented |
| Multi-user auth | Not in scope for self-hosted HA add-on |

---

## Current State Summary

| Category | Count |
|----------|-------|
| Features requiring validation | 38 |
| Features in VS-1 (current) | 10 |
| Features in VS-2 | 13 |
| Features in VS-3 | 9 |
| Features in VS-4 | 6 |
| Known issues (code audit) | 9 |
| HIGH severity issues | 1 (KI-001) |

---

## Deliverables

After all 4 sessions pass:
- [ ] `RC1_RUNTIME_VALIDATION.md` — final verdict with all evidence compiled
- [ ] `RELEASE_STATUS.md` — updated gate status
- [ ] `KNOWN_ISSUES.md` — updated with any runtime-discovered issues
- [ ] `CHANGELOG.md` — updated with any fixes required during validation

---

*Proceed to VS-1: `RC1_VALIDATION_CHECKLIST.md`*
