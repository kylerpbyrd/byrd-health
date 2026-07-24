# ADR-0003: Database Strategy

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Data persistence layer                         |

---

## 1. Context

Byrd Health stores sensitive health data including basal body temperatures, fertility signs, cycle history, and computed insights. The data layer must:

- Work with SQLite for HA Add-on deployment (zero-config, local)
- Support PostgreSQL for future ByrdOS deployment (multi-user, scalable)
- Support forward-only, versioned schema migrations
- Maintain referential integrity with foreign keys
- Allow future encryption at rest (Phase 2+)
- Be engine-agnostic (same code, different database)

The legacy application uses raw SQL via Python's `sqlite3` module with a migration framework that exists but is unused (only placeholder migration). This approach is not engine-portable and lacks type safety.

## 2. Decision

Use **SQLAlchemy 2.0** for ORM with **Alembic** for schema migrations.

### 2.1 Engine Strategy

| Deployment        | Engine     | Rationale                                     |
|-------------------|------------|-----------------------------------------------|
| Development       | SQLite     | Zero setup, fast iteration                    |
| HA Add-on         | SQLite (WAL)| Zero-config, filesystem-local, sufficient     |
| ByrdOS (single)   | SQLite (WAL)| Same as HA Add-on                             |
| ByrdOS (multi)    | PostgreSQL 16+ | Concurrent writes, connection pooling     |

### 2.2 SQLAlchemy Configuration

```python
# Engine selection via environment variable or config
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/byrd_health.db")

engine = create_async_engine(DATABASE_URL, echo=False)
```

For SQLite, enable WAL mode and foreign keys:

```python
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### 2.3 Model Design Principles

- All models inherit from SQLAlchemy `DeclarativeBase`
- Use `Mapped` type annotations for column definitions
- UUID primary keys (not autoincrement integers) for future multi-instance compatibility
- Foreign keys with CASCADE deletes on appropriate relationships
- `created_at` / `updated_at` timestamps on all tables
- Enum fields use Python `StrEnum` for type safety
- No raw SQL in application code — all queries through ORM

### 2.4 Encryption Deferral (Phase 2)

Per decision: encryption at rest is deferred to Phase 2. Phase 1 must:

- Design columns with encryption boundaries in mind
- Avoid exposing raw sensitive data in logs or API responses
- Document which columns will require encryption (temperature values, fertility observations, symptom data)
- Keep encryption-ready column types (TEXT/BLOB, not constrained types)

## 3. Schema (Phase 1)

### 3.1 Core Tables

| Table              | Purpose                            | Key Relationships                     |
|--------------------|------------------------------------|---------------------------------------|
| `profiles`         | User profiles                      | One-to-many with cycles               |
| `cycles`           | Menstrual cycles                   | FK to profiles; one-to-many with temps, signs, symptoms |
| `temperatures`     | BBT readings                       | FK to cycles; unique (cycle_id, date) |
| `fertility_signs`  | Daily fertility observations       | FK to cycles; unique (cycle_id, date) |
| `symptoms`         | Per-day symptoms                   | FK to cycles                          |
| `computed_insights`| Cached analysis results            | FK to cycles; unique (cycle_id)       |

### 3.2 Migration Versioning

- Version `001` — Initial schema (Phase 1)
- Alembic auto-generation for new columns/tables
- Manual review required for all auto-generated migrations
- Forward-only migrations — no rollback in production

## 4. Consequences

### Positive
- Engine-agnostic — SQLite for HA, PostgreSQL for ByrdOS
- Type-safe queries with SQLAlchemy 2.0 style
- Alembic provides robust migration tooling
- Prepared for encryption in Phase 2

### Negative
- SQLAlchemy adds learning curve vs. raw SQL
- Async SQLAlchemy has specific patterns (greenlet, session management)
- UUID primary keys are larger than integers (minor space concern for SQLite)

### Risks
- SQLite/PostgreSQL behavioral differences (datetime handling, JSON columns) — mitigated by testing on both engines
- Migration complexity with Alembic auto-generation — mitigated by mandatory manual review

## 5. References

- `docs/ARCHITECTURE_RECOMMENDATIONS.md §5` — Database strategy
- `docs/LEGACY_REVIEW.md §5` — Legacy database design analysis
- `ADR-0001` — Platform architecture
- `ADR-0004` — User/profile model
