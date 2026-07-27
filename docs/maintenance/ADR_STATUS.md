# ADR Status

All 13 Architecture Decision Records audited for implementation status.

## Implemented (7)

| ADR | Title | Phase | Notes |
|-----|-------|-------|-------|
| 0001 | Platform Architecture | 1 | Foundation |
| 0002 | Frontend Architecture | 1 | — |
| 0003 | Database Strategy | 1 | — |
| 0004 | User Profile Model | 1 | — |
| 0006 | HA Integration Boundary | 2 | — |
| 0007 | AI Prediction Architecture | 2 | — |
| 0010 | Graphify Knowledge | 3 | — |
| 0012 | WebSocket Architecture | 3 | — |

## Partially Implemented (5)

| ADR | Title | Phase | Discrepancies |
|-----|-------|-------|---------------|
| 0005 | Legacy Migration | 2 | `writer.py` never created; tool outputs JSON instead |
| 0008 | Security/Privacy | 2 | HKDF not used (uses SHA-256); `pip-audit` not in CI |
| 0009 | Testing Strategy | 2 | No coverage enforcement; no Hypothesis; mypy not strict |
| 0011 | Device Adapter Pattern | 3 | Endpoint mismatch: ADR says `POST /devices/{id}/read`, actual is `POST /devices/read` |
| 0013 | Container Distribution | 3 | No GHCR publishing CI; only amd64 built; no versioned tags |

## Not Implemented (0)

All ADRs have at least partial implementation.
