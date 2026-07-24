from __future__ import annotations

import uuid


def _int_to_bool(value: int | None, default: bool = False) -> bool:
    """Convert legacy integer boolean (0/1) to Python bool."""
    if value is None:
        return default
    return bool(int(value))


def _empty_to_none(value: str | None) -> str | None:
    """Convert empty string to None for nullable text fields."""
    if value is None or value == "":
        return None
    return value


def _build_id_map(legacy_rows: list[dict]) -> dict[int, str]:
    """Build {old_int_id: new_uuid_str} mapping for a table."""
    return {row["id"]: str(uuid.uuid4()) for row in legacy_rows}


def transform_profiles(legacy_profiles: list[dict]) -> tuple[list[dict], dict[int, str]]:
    """Transform legacy profiles and return (transformed, id_map)."""
    id_map = _build_id_map(legacy_profiles)
    result = []
    for p in legacy_profiles:
        result.append(
            {
                "id": id_map[p["id"]],
                "name": p["name"],
                "slug": p["slug"],
                "temp_unit": p.get("temp_unit", "F"),
                "interpretation_method": p.get("interpretation_method", "standard"),
                "is_active": _int_to_bool(p.get("active"), default=False),
                "created_at": p.get("created_at"),
                "updated_at": None,
            }
        )
    return result, id_map


def transform_cycles(
    legacy_cycles: list[dict],
    profile_id_map: dict[int, str],
) -> tuple[list[dict], dict[int, str]]:
    """Transform cycles with remapped profile FKs."""
    id_map = _build_id_map(legacy_cycles)
    result = []
    for c in legacy_cycles:
        old_pid = c["profile_id"]
        result.append(
            {
                "id": id_map[c["id"]],
                "profile_id": profile_id_map.get(old_pid, str(uuid.uuid4())),
                "start_date": c["start_date"],
                "end_date": _empty_to_none(c.get("end_date")),
                "cycle_length": c.get("cycle_length"),
                "notes": c.get("notes", ""),
            }
        )
    return result, id_map


def transform_temperatures(
    legacy_temps: list[dict],
    cycle_id_map: dict[int, str],
) -> tuple[list[dict], dict[int, str]]:
    """Transform temperatures with remapped cycle FKs."""
    id_map = _build_id_map(legacy_temps)
    result = []
    for t in legacy_temps:
        old_cid = t["cycle_id"]
        result.append(
            {
                "id": id_map[t["id"]],
                "cycle_id": cycle_id_map.get(old_cid, str(uuid.uuid4())),
                "date": t["date"],
                "temp_value": t["temp_value"],
                "time_taken": _empty_to_none(t.get("time_taken")),
                "is_discarded": _int_to_bool(t.get("is_discarded")),
                "discard_reason": t.get("discard_reason", ""),
                "notes": t.get("notes", ""),
            }
        )
    return result, id_map


def transform_fertility_signs(
    legacy_signs: list[dict],
    cycle_id_map: dict[int, str],
) -> tuple[list[dict], dict[int, str]]:
    """Transform fertility signs with remapped cycle FKs."""
    id_map = _build_id_map(legacy_signs)
    result = []
    for s in legacy_signs:
        old_cid = s["cycle_id"]
        result.append(
            {
                "id": id_map[s["id"]],
                "cycle_id": cycle_id_map.get(old_cid, str(uuid.uuid4())),
                "date": s["date"],
                "menstrual_flow": s.get("menstrual_flow", ""),
                "cervical_mucus": s.get("cervical_mucus", ""),
                "cervical_position": s.get("cervical_position", ""),
                "cervical_firmness": s.get("cervical_firmness", ""),
                "cervical_opening": s.get("cervical_opening", ""),
                "opk_result": s.get("opk_result", ""),
                "notes": s.get("notes", ""),
            }
        )
    return result, id_map


def transform_symptoms(
    legacy_symptoms: list[dict],
    cycle_id_map: dict[int, str],
) -> tuple[list[dict], dict[int, str]]:
    """Transform symptoms with remapped cycle FKs.

    Note: legacy `notes` field is dropped — the new Symptom model
    does not include a notes column.
    """
    id_map = _build_id_map(legacy_symptoms)
    result = []
    for s in legacy_symptoms:
        old_cid = s["cycle_id"]
        result.append(
            {
                "id": id_map[s["id"]],
                "cycle_id": cycle_id_map.get(old_cid, str(uuid.uuid4())),
                "date": s["date"],
                "symptom_type": s["symptom_type"],
                "severity": s.get("severity", 1),
            }
        )
    return result, id_map


def transform_computed_insights(
    legacy_insights: list[dict],
    cycle_id_map: dict[int, str],
) -> tuple[list[dict], dict[int, str]]:
    """Transform computed insights with remapped cycle FKs.

    Adds engine_version = "1.0.0-legacy" since legacy had no version field.
    """
    id_map = _build_id_map(legacy_insights)
    result = []
    for ci in legacy_insights:
        old_cid = ci["cycle_id"]
        result.append(
            {
                "id": id_map[ci["id"]],
                "cycle_id": cycle_id_map.get(old_cid, str(uuid.uuid4())),
                "coverline": ci.get("coverline"),
                "ovulation_date": _empty_to_none(ci.get("ovulation_date")),
                "ovulation_confirmed": _int_to_bool(ci.get("ovulation_confirmed")),
                "ovulation_method": ci.get("ovulation_method", ""),
                "fertile_start_date": _empty_to_none(ci.get("fertile_start_date")),
                "fertile_end_date": _empty_to_none(ci.get("fertile_end_date")),
                "post_ovulatory_infertile_date": _empty_to_none(
                    ci.get("post_ovulatory_infertile_date")
                ),
                "luteal_length": ci.get("luteal_length"),
                "luteal_phase_short": _int_to_bool(ci.get("luteal_phase_short")),
                "pregnancy_indicator": _int_to_bool(ci.get("pregnancy_indicator")),
                "consecutive_elevated_temps": ci.get("consecutive_elevated_temps", 0),
                "engine_version": "1.0.0-legacy",
                "computed_at": ci.get("computed_at"),
            }
        )
    return result, id_map
