# ADR-0004: User/Profile Model

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Identity and data ownership model              |

---

## 1. Context

Byrd Health stores reproductive health data that must be clearly owned and isolated. The initial deployment targets personal/family self-hosted use, with future ByrdOS multi-user deployment.

The legacy application supports "profiles" — multiple named profiles within a single database, with an active/inactive toggle. Profile data is scoped per-profile, and profile switching is done via the web UI.

Requirements:
- v1 (now): Multi-profile within single deployment (personal/family)
- Future: Multi-user isolation for ByrdOS
- Data must be clearly owned by a profile
- Profile switching must not expose cross-profile data
- Design must not preclude future multi-user migration

## 2. Decision

Implement **multi-profile architecture** for v1, with the data model designed to support future multi-user isolation without schema changes.

### 2.1 Profile Model

```python
class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    temp_unit: Mapped[TempUnit] = mapped_column(String(1), default=TempUnit.F)
    interpretation_method: Mapped[InterpretationMethod] = mapped_column(
        String(16), default=InterpretationMethod.STANDARD
    )
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    cycles: Mapped[list["Cycle"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
```

Key design decisions:
- UUID primary key — enables multi-instance data merging in the future
- `slug` field — URL/entity-safe identifier (preserved from legacy)
- `is_active` — session-based active profile selection (v1 pattern)
- No password/auth fields — authentication is external (HA Ingress or ByrdOS auth)
- `temp_unit` and `interpretation_method` are per-profile settings (preserved from legacy)

### 2.2 Data Ownership

All health data is owned by a profile through foreign key relationships:

```
Profile (1) ──── (N) Cycle ──── (N) Temperature
                              ─── (N) FertilitySigns
                              ─── (N) Symptoms
                              ─── (1) ComputedInsights
```

All queries MUST filter by profile_id. The data service layer enforces this at the repository level:

```python
class CycleRepository:
    async def get_cycles(self, profile_id: UUID) -> list[Cycle]: ...
    async def get_cycle(self, cycle_id: UUID, profile_id: UUID) -> Cycle | None: ...
```

### 2.3 Future Multi-User Path

When ByrdOS multi-user support is needed:

| v1 (Multi-Profile)          | v2 (Multi-User)                  |
|-----------------------------|----------------------------------|
| Single DB, multiple profiles| Per-user database or schema     |
| Session-based profile switch| Auth-gated user isolation       |
| `is_active` flag in profiles | User-to-profile mapping table   |
| No auth in app              | OAuth2/OIDC integration         |

The transition path is additive — add a `user_accounts` table with a foreign key to profiles, add auth middleware, and isolate data access by authenticated user. The profile model does not need to change.

## 3. Consequences

### Positive
- Simple for v1 deployment (personal/family use)
- Profile-based data isolation already proven in legacy app
- UUID primary keys enable future data portability
- Clear path to multi-user without schema breaking changes

### Negative
- No authentication in Phase 1 — relies entirely on deployment environment (HA Ingress)
- Profile switching via UI toggle is not secure for hostile multi-user environments (acceptable for v1 scope)

### Risks
- Users may expect multi-user auth in v1 — mitigated by clear documentation that v1 is personal/family only
- UUID-based profile IDs may be less intuitive in logs than integer IDs — mitigated by including `slug` in log context

## 4. References

- `docs/LEGACY_REVIEW.md §5.1` — Legacy profile table design
- `docs/ARCHITECTURE_RECOMMENDATIONS.md §12.2` — Authentication model
- `ADR-0001` — Platform architecture
- `ADR-0003` — Database strategy
