# ADR-0008: Security and Privacy Model

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Entire Byrd Health platform                    |

---

## 1. Context

Byrd Health processes sensitive reproductive health data. The platform must protect this data at every layer while remaining practical for self-hosted deployment.

Security posture by deployment target:

| Concern         | HA Add-on (Phase 2-3)              | ByrdOS (Future)                |
|-----------------|-----------------------------------|--------------------------------|
| Authentication  | HA Ingress proxy                  | ByrdOS unified auth (OAuth2)   |
| Transport       | HA Ingress (HTTPS)                | TLS termination                |
| Data at rest    | Filesystem (Phase 1); encrypted (Phase 2) | Encrypted at rest     |
| Secrets         | HA Supervisor secrets / env vars  | ByrdOS keychain                |
| Multi-tenancy   | Profile-level within DB           | User-level with isolation      |

## 2. Decision

### 2.1 Phase 1 Security Posture

Phase 1 is the **platform foundation phase** — deployed only in development, not in production. Security is designed but not fully implemented.

| Layer           | Phase 1 Implementation                              |
|-----------------|-----------------------------------------------------|
| Transport       | None (local development only)                       |
| Authentication  | None (development mode)                             |
| Data at rest    | Plaintext SQLite (development data only)            |
| Secrets         | Environment variables (development)                 |
| CSRF            | Disabled in dev; designed for SPA tokens            |
| CORS            | Permissive in dev; restrictive config for production|
| Input validation| Pydantic validation on all endpoints                |
| SQL injection   | Mitigated by SQLAlchemy ORM (parameterized queries) |
| XSS             | Mitigated by React (auto-escaping)                  |
| Dependency audit| CI pipeline (`pip-audit`, `npm audit`)              |

### 2.2 Phase 2+ Security Model

When deploying to Home Assistant Add-on (Phase 2), the security model activates:

| Layer           | Phase 2+ Implementation                             |
|-----------------|-----------------------------------------------------|
| Transport       | HA Ingress proxy provides HTTPS                     |
| Authentication  | Relies on HA Ingress access control                 |
| Data at rest    | AES-256-GCM per-profile encryption at application layer |
| Secrets         | SUPERVISOR_TOKEN from HA Supervisor; encryption keys from HA secrets |
| CSRF            | SPA token pattern for form submissions              |
| API auth        | API key for HA automation scripts                   |
| Audit logging   | Profile-scoped access and modification events       |

### 2.3 Encryption Architecture (Phase 2)

When encryption is implemented:

```
Master Key (from HA secrets / ByrdOS keychain)
        │
        ▼
    Key derivation (HKDF)
        │
        ▼
    Profile Encryption Keys (per-profile, stored encrypted)
        │
        ▼
    Column-level encryption for:
      - Temperature values
      - Fertility observations
      - Symptom data
      - Notes (user-entered text)
```

Encrypted columns use AES-256-GCM with per-row initialization vectors. Decryption happens in the Data Service layer. The API layer never handles encryption directly.

### 2.4 Privacy Principles

1. **Local processing** — All analysis runs locally. No data leaves the device.
2. **No telemetry** — No usage data, crash reports, or analytics are sent externally.
3. **Data ownership** — Users own their data. Export is always available in open formats.
4. **Minimal collection** — Only data the user explicitly enters or authorizes (device readings).
5. **Transparency** — All data flows are documented. Privacy policy is human-readable.
6. **No cloud dependencies** — The platform operates fully offline after installation.
7. **No vendor lock-in** — Data export in portable JSON format; standard database engines.

### 2.5 Data Export Format

```json
{
  "format": "byrd-health-export",
  "version": 1,
  "exported_at": "2026-07-23T12:00:00",
  "profile": { "slug": "...", "name": "..." },
  "cycles": [ ... ],
  "temperatures": [ ... ],
  "fertility_signs": [ ... ],
  "symptoms": [ ... ],
  "insights": [ ... ]
}
```

Compatible with the legacy format (`bbt-fertility-tracker-export` v1) where fields overlap. New fields are additive.

## 3. Consequences

### Positive
- Phase 1 design accounts for security without blocking development
- Phase 2 encryption is planned but not prematurely implemented
- Privacy principles are documented and enforceable
- No external dependencies for core functionality

### Negative
- Plaintext data in Phase 1 development — developers must use synthetic/test data only
- No auth in Phase 1 means the API is open during development
- Application-layer encryption adds complexity in Phase 2

### Risks
- Developers might use real health data in Phase 1 — mitigated by documentation and synthetic data generators
- Encryption performance impact on SQLite — mitigated by benchmarking and selective column encryption
- Key management complexity — mitigated by using the deployment environment's secret management (HA secrets, ByrdOS keychain)

## 4. References

- `docs/LEGACY_REVIEW.md §11` — Legacy security concerns
- `docs/ARCHITECTURE_RECOMMENDATIONS.md §12` — Security architecture recommendations
- `ADR-0001` — Platform architecture
- `ADR-0003` — Database strategy (encryption deferral)
