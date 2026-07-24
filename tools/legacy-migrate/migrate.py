#!/usr/bin/env python3
"""Legacy BBT data migration tool for Byrd Health.

Reads a legacy bbt.db SQLite database, validates data, transforms
the schema (integer IDs -> UUIDs, remapped FKs), and outputs JSON
compatible with the Byrd Health import endpoint.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

try:
    from .reader import read_legacy_db
    from .transformer import (
        transform_computed_insights,
        transform_cycles,
        transform_fertility_signs,
        transform_profiles,
        transform_symptoms,
        transform_temperatures,
    )
    from .validator import validate_legacy_data
except ImportError:
    from reader import read_legacy_db  # type: ignore[no-redef]
    from transformer import (  # type: ignore[no-redef]
        transform_computed_insights,
        transform_cycles,
        transform_fertility_signs,
        transform_profiles,
        transform_symptoms,
        transform_temperatures,
    )
    from validator import validate_legacy_data  # type: ignore[no-redef]


def _report_issues(issues: dict[str, list[str]]) -> None:
    """Print validation issues to stderr."""
    errors = issues.get("error", [])
    warnings = issues.get("warning", [])

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):", file=sys.stderr)
        for w in warnings:
            print(f"    - {w}", file=sys.stderr)

    if errors:
        print(f"\n  Errors ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"    - {e}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Migrate legacy BBT data to Byrd Health format",
    )
    parser.add_argument(
        "input",
        help="Path to legacy bbt.db",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="byrd_health_import.json",
        help="Output JSON file (default: byrd_health_import.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without writing output",
    )
    parser.add_argument(
        "--profile",
        help="Migrate only a specific profile (by name or slug)",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.input)
    if not db_path.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # 1. Read
    print(f"Reading legacy database: {db_path}")
    data = read_legacy_db(db_path)
    for table, rows in data.items():
        print(f"  {table}: {len(rows)} rows")

    # 2. Validate
    print("\nValidating data...")
    issues = validate_legacy_data(data)
    _report_issues(issues)

    errors = issues.get("error", [])
    if errors:
        print(
            f"\nMigration blocked: {len(errors)} validation error(s). "
            "Fix the legacy data and try again.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Filter by profile if requested
    profiles = data.get("profiles", [])
    if args.profile:
        profile_name = args.profile
        profiles = [
            p
            for p in profiles
            if p.get("name") == profile_name or p.get("slug") == profile_name
        ]
        if not profiles:
            print(
                f"Error: profile '{profile_name}' not found in legacy database.",
                file=sys.stderr,
            )
            sys.exit(1)
        profile_ids = {p["id"] for p in profiles}
        data["cycles"] = [
            c for c in data.get("cycles", []) if c["profile_id"] in profile_ids
        ]
        cycle_ids = {c["id"] for c in data["cycles"]}
        data["temperatures"] = [
            t for t in data.get("temperatures", []) if t["cycle_id"] in cycle_ids
        ]
        data["fertility_signs"] = [
            s for s in data.get("fertility_signs", []) if s["cycle_id"] in cycle_ids
        ]
        data["symptoms"] = [
            s for s in data.get("symptoms", []) if s["cycle_id"] in cycle_ids
        ]
        data["computed_insights"] = [
            ci
            for ci in data.get("computed_insights", [])
            if ci["cycle_id"] in cycle_ids
        ]
        print(f"  Filtering to profile: {args.profile}")

    # 4. Transform
    print("\nTransforming schema...")
    out_profiles, profile_id_map = transform_profiles(profiles)
    out_cycles, cycle_id_map = transform_cycles(data.get("cycles", []), profile_id_map)
    out_temps, temp_id_map = transform_temperatures(
        data.get("temperatures", []), cycle_id_map
    )
    out_signs, signs_id_map = transform_fertility_signs(
        data.get("fertility_signs", []), cycle_id_map
    )
    out_symptoms, symptoms_id_map = transform_symptoms(
        data.get("symptoms", []), cycle_id_map
    )
    out_insights, insights_id_map = transform_computed_insights(
        data.get("computed_insights", []), cycle_id_map
    )

    output = {
        "format": "byrd-health-import",
        "version": 1,
        "migrated_at": datetime.now(UTC).isoformat(),
        "source": "bbt-fertility-tracker-legacy",
        "profiles": out_profiles,
        "cycles": out_cycles,
        "temperatures": out_temps,
        "fertility_signs": out_signs,
        "symptoms": out_symptoms,
        "computed_insights": out_insights,
        "id_mappings": {
            "profiles": {str(k): v for k, v in profile_id_map.items()},
            "cycles": {str(k): v for k, v in cycle_id_map.items()},
            "temperatures": {str(k): v for k, v in temp_id_map.items()},
            "fertility_signs": {str(k): v for k, v in signs_id_map.items()},
            "symptoms": {str(k): v for k, v in symptoms_id_map.items()},
            "computed_insights": {str(k): v for k, v in insights_id_map.items()},
        },
    }

    # 5. Output
    if args.dry_run:
        print("\nDry run complete. No file written.")
        print(f"  Profiles:     {len(out_profiles)}")
        print(f"  Cycles:       {len(out_cycles)}")
        print(f"  Temperatures: {len(out_temps)}")
        print(f"  Fert. Signs:  {len(out_signs)}")
        print(f"  Symptoms:     {len(out_symptoms)}")
        print(f"  Insights:     {len(out_insights)}")
        print(f"  Total:        {sum(len(v) for v in output.values() if isinstance(v, list))} records")
        return

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nMigration written to: {out_path}")
    print(f"  Profiles:     {len(out_profiles)}")
    print(f"  Cycles:       {len(out_cycles)}")
    print(f"  Temperatures: {len(out_temps)}")
    print(f"  Fert. Signs:  {len(out_signs)}")
    print(f"  Symptoms:     {len(out_symptoms)}")
    print(f"  Insights:     {len(out_insights)}")


if __name__ == "__main__":
    main()
