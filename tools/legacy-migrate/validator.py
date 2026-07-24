from __future__ import annotations

import re
from collections import defaultdict

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

BBT_MIN = 30.0
BBT_MAX = 110.0


def validate_legacy_data(data: dict[str, list[dict]]) -> dict[str, list[str]]:
    """Validate legacy data and return {level: [messages]}.

    levels: "error" (blocks migration), "warning" (informational).

    Checks performed:
    - Profile name uniqueness
    - Cycle FKs reference valid profile IDs
    - Temperature, sign, symptom, insight FKs reference valid cycle IDs
    - Date formats (YYYY-MM-DD)
    - Temperature values in plausible BBT range
    - Duplicate (cycle_id, date) pairs in temperatures and fertility_signs
    """
    errors: list[str] = []
    warnings: list[str] = []

    profiles = data.get("profiles", [])
    cycles = data.get("cycles", [])
    temperatures = data.get("temperatures", [])
    signs = data.get("fertility_signs", [])
    symptoms = data.get("symptoms", [])
    insights = data.get("computed_insights", [])

    profile_ids = {p["id"] for p in profiles}
    profile_names = [p.get("name", "") for p in profiles]
    cycle_ids = {c["id"] for c in cycles}

    if not profiles:
        warnings.append("No profiles found in legacy database.")

    # --- Profile uniqueness ---
    name_counts: dict[str, int] = defaultdict(int)
    for name in profile_names:
        name_counts[name] += 1
    for name, count in name_counts.items():
        if count > 1:
            errors.append(f"Duplicate profile name '{name}' found {count} times.")

    # --- Cycle FK validation ---
    for c in cycles:
        pid = c.get("profile_id")
        if pid and pid not in profile_ids:
            errors.append(
                f"Cycle id={c['id']} references non-existent profile_id={pid}."
            )

    # --- FK validation for child tables ---
    def _check_cycle_fks(
        rows: list[dict],
        label: str,
        cycle_ids: set[int],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        seen_dates: set[tuple[int, str]] = set()
        for row in rows:
            cid = row.get("cycle_id")
            if cid and cid not in cycle_ids:
                errors.append(
                    f"{label} id={row['id']} references non-existent cycle_id={cid}."
                )
            date_val = row.get("date", "")
            if date_val and not DATE_RE.match(str(date_val)):
                errors.append(
                    f"{label} id={row['id']} has invalid date format: '{date_val}'."
                )
            if cid and date_val:
                key = (int(cid), str(date_val))
                if key in seen_dates:
                    warnings.append(
                        f"Duplicate ({label}) entry for cycle_id={cid}, date={date_val}."
                    )
                seen_dates.add(key)

    _check_cycle_fks(temperatures, "Temperature", cycle_ids, errors, warnings)
    _check_cycle_fks(signs, "FertilitySigns", cycle_ids, errors, warnings)

    # Symptoms FK check (no unique constraint on cycle_id+date)
    for s in symptoms:
        cid = s.get("cycle_id")
        if cid and cid not in cycle_ids:
            errors.append(
                f"Symptom id={s['id']} references non-existent cycle_id={cid}."
            )
        date_val = s.get("date", "")
        if date_val and not DATE_RE.match(str(date_val)):
            errors.append(
                f"Symptom id={s['id']} has invalid date format: '{date_val}'."
            )

    # Computed insights FK check
    for ci in insights:
        cid = ci.get("cycle_id")
        if cid and cid not in cycle_ids:
            errors.append(
                f"ComputedInsights id={ci['id']} references non-existent cycle_id={cid}."
            )

    # --- Temperature range ---
    for t in temperatures:
        val = t.get("temp_value")
        if val is not None:
            try:
                fval = float(val)
                if fval < BBT_MIN or fval > BBT_MAX:
                    warnings.append(
                        f"Temperature id={t['id']} has implausible value {fval} "
                        f"(expected {BBT_MIN}-{BBT_MAX})."
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"Temperature id={t['id']} has non-numeric temp_value: '{val}'."
                )

    # --- Cycles must have start_date ---
    for c in cycles:
        sd = c.get("start_date", "")
        if not sd or not DATE_RE.match(str(sd)):
            errors.append(
                f"Cycle id={c['id']} has missing or invalid start_date: '{sd}'."
            )

    return {"error": errors, "warning": warnings}
