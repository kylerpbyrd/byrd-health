# Legacy Data Migration Tool

Migrate data from the legacy BBT Fertility Tracker to Byrd Health.

## Prerequisites

- Python 3.12+
- A legacy `bbt.db` file from the BBT Fertility Tracker (Home Assistant add-on)

## Usage

```bash
# Preview migration (dry-run — validates data without writing output)
python -m tools.legacy-migrate.migrate /path/to/bbt.db --dry-run

# Migrate all data
python -m tools.legacy-migrate.migrate /path/to/bbt.db -o migrated_data.json

# Migrate specific profile
python -m tools.legacy-migrate.migrate /path/to/bbt.db --profile Alice
```

## Options

| Flag | Description |
|---|---|
| `--output`, `-o` | Output JSON file path (default: `byrd_health_import.json`) |
| `--dry-run` | Validate data only; do not write output |
| `--profile` | Filter to a single profile by name or slug |

## What Gets Migrated

| Legacy Table | New Table | Key Changes |
|---|---|---|
| `profiles` | `profiles` | Integer ID → UUID; `active` → `is_active`; `ha_sensor_entity` dropped |
| `cycles` | `cycles` | Integer ID → UUID; `profile_id` remapped |
| `temperatures` | `temperatures` | Integer ID → UUID; `cycle_id` remapped; empty `time_taken` → null |
| `fertility_signs` | `fertility_signs` | Integer ID → UUID; `cycle_id` remapped |
| `symptoms` | `symptoms` | Integer ID → UUID; `cycle_id` remapped; `notes` field dropped |
| `computed_insights` | `computed_insights` | Integer ID → UUID; `cycle_id` remapped; `engine_version` set to `1.0.0-legacy` |

## What Is NOT Migrated

- `settings` table — replaced by profile model fields in the new platform
- `schema_migrations` table — replaced by Alembic
- Lovelace card registration state — not data

## Output Format

The output JSON follows the `byrd-health-import` format (v1):

```json
{
  "format": "byrd-health-import",
  "version": 1,
  "migrated_at": "2026-07-24T00:00:00+00:00",
  "source": "bbt-fertility-tracker-legacy",
  "profiles": [...],
  "cycles": [...],
  "temperatures": [...],
  "fertility_signs": [...],
  "symptoms": [...],
  "computed_insights": [...],
  "id_mappings": {
    "profiles": {"1": "uuid-here", ...},
    "cycles": {"1": "uuid-here", ...}
  }
}
```

The `id_mappings` section records the old-to-new ID translation for auditing.

## Validation

The tool performs these checks before migration:

- Profile name uniqueness
- Foreign key integrity (cycles → profiles, child records → cycles)
- Date format validation (YYYY-MM-DD)
- Temperature plausibility (30.0–110.0 range covering both F and C)
- Duplicate (cycle_id, date) detection

Validation errors block migration. Warnings are informational.
