# Documentation Audit

60 documents inventoried. Each classified by status and recommended action.

## Documents to UPDATE (12)

| Document | Issue |
|----------|-------|
| `README.md` | ADR count 12 → 13; phase status outdated |
| `ARCHITECTURE.md` | Add ADR-0013 |
| `FEATURES.md` | Add Phase 3 |
| `DEVELOPER_GUIDE.md` | 5 packages, not 3 |
| `USER_GUIDE.md` | Add Phase 3 device config |
| `TROUBLESHOOTING.md` | Add Phase 3 issues |
| `ADR-0011` | Fix endpoint mismatch |
| `KNOWN_ISSUES.md` | Refresh against current state |
| `tools/legacy-migrate/README.md` | Update for JSON output change |
| `ADR-0008` | Encryption implementation claim incorrect |

## Documents to ARCHIVE (10)

| Document | Reason |
|----------|--------|
| `PROMPT.md` | Superseded by AGENTS.md |
| `MILESTONE_GUIDE.md` | Internal process, no longer relevant |
| `PHASE3_PLAN.md` | Phase 3 complete |
| `RELEASE_HANDOFF.md` | One-time artifact |
| `RELEASE_CANDIDATE_VALIDATION.md` | One-time artifact |
| `SESSION_HANDOFF.md` | One-time artifact |
| `RUNTIME_READINESS_REPORT.md` | One-time artifact |
| `RC1_RUNTIME_VALIDATION.md` | One-time artifact |
| Top-level `RELEASE_HANDOFF.md` | One-time artifact |

## Documents to DELETE/POPULATE

| Document | Issue |
|----------|-------|
| `PROJECT_IDEA.md` | Empty (0 bytes) — either populate with vision or delete |

## Key Contradictions

- **Phase status:** README says Phase 2, CHANGELOG confirms Phase 3 is complete
- **ADR count:** README and ARCHITECTURE.md say 12, actual count is 13
- **Entity naming:** `RELEASE_HANDOFF` says `byrd_health_` prefix, actual Home Assistant prefix is `bbt_`
- **ADR-0011 endpoint:** Specification says `POST /devices/{id}/read`, implementation is `POST /devices/read`

## Summary Table

Statuses: Current / Needs Updating / Duplicate / Obsolete / Archive Candidate

Actions: Keep / Update / Archive / Delete

*(Full 60-document table omitted for brevity — key documents listed above.)*
