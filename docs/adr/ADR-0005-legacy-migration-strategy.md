# ADR-0005: Legacy Migration Strategy

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Data migration from legacy BBT Fertility Tracker|

---

## 1. Context

The legacy BBT Fertility Tracker stores user data in a SQLite database (`/data/bbt.db`) with a well-defined schema. Existing users have accumulated cycles, temperatures, and fertility observations.

The new Byrd Health platform uses SQLAlchemy with a redesigned schema (UUID keys, new column types, Alembic migrations). Direct schema compatibility is not possible.

Requirements:
- Existing users must be able to migrate their data
- Migration must be safe (validation, preview, rollback)
- Migration must not couple the new platform to legacy structures
- Migration tooling must be separate from the core platform

## 2. Decision

Provide a **standalone migration utility** that reads legacy `bbt.db`, validates data, transforms schema, and imports supported records into the new platform.

### 2.1 Tool Design

```
tools/legacy-migrate/
├── migrate.py              # Entry point
├── reader.py               # Legacy SQLite reader
├── transformer.py          # Schema transformation logic
├── validator.py            # Data validation rules
├── writer.py               # New platform writer (via Data Service API)
└── README.md               # Usage instructions
```

### 2.2 Migration Process

```
Legacy bbt.db
     │
     ▼
┌──────────┐    ┌───────────┐    ┌──────────┐    ┌─────────────┐
│  Read    │───►│  Validate │───►│ Transform│───►│  Write to   │
│ Legacy   │    │  Data     │    │ Schema   │    │  New Platform│
└──────────┘    └───────────┘    └──────────┘    └─────────────┘
                                                       │
                                                       ▼
                                                byrd_health.db
```

### 2.3 Mapping Strategy

| Legacy Table        | New Table           | Transformation                               |
|---------------------|---------------------|----------------------------------------------|
| `profiles`          | `profiles`          | Integer ID → UUID; preserve name, slug, settings |
| `cycles`            | `cycles`            | Integer ID → UUID; remap profile_id FK       |
| `temperatures`      | `temperatures`      | Integer ID → UUID; remap cycle_id FK         |
| `fertility_signs`   | `fertility_signs`   | Integer ID → UUID; remap cycle_id FK         |
| `symptoms`          | `symptoms`          | Integer ID → UUID; remap cycle_id FK         |
| `computed_insights` | `computed_insights` | Integer ID → UUID; remap cycle_id FK; add engine_version |

### 2.4 Features

- **Dry-run mode:** Preview migration without writing
- **Validation reports:** Flag data issues before migration
- **Profile selection:** Migrate specific profiles
- **Resume support:** Skip already-migrated data
- **Export backup:** Create a JSON backup of legacy data as a side effect

### 2.5 What Is NOT Migrated

- `settings` table (legacy key-value settings) — replaced by profile model fields
- `schema_migrations` table — replaced by Alembic
- Lovelace card registration state — not data, handled by HA Bridge

## 3. Consequences

### Positive
- No legacy coupling in core platform code
- Migration tool can be developed and tested independently
- Dry-run provides safety for users
- JSON export as side effect provides backup

### Negative
- Separate tool requires maintenance
- Migration adds a step for existing users
- UUID generation means direct ID comparison between old and new data is not possible

### Risks
- Legacy data may contain values outside new validation rules — mitigated by validation step with clear error reporting
- Large datasets may make migration slow — mitigated by batching and progress reporting
- Users may attempt migration before reading documentation — mitigated by clear prerequisites in tool output

## 4. Implementation Timing

The migration utility is developed in **Phase 2** (after core platform is stable). Phase 1 does not include migration tooling.

During Phase 1, the new platform starts with a fresh database. The legacy `bbt.db` schema is referenced for data model design but not imported.

## 5. References

- `docs/LEGACY_REVIEW.md §5` — Legacy schema design
- `docs/MIGRATION_PLAN.md §4` — Data migration strategy
- `ADR-0003` — Database strategy
- `ADR-0004` — User/profile model
