from datetime import date

from fertility_engine.fertile_window import compute_fertile_window
from fertility_engine.models import (
    CycleInsights,
    FertilitySignsRecord,
    OvulationResult,
    ProfileSettings,
    TemperatureRecord,
)
from fertility_engine.ovulation import detect_ovulation


def _to_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _count_consecutive_elevated(
    temps: list[dict], coverline: float, after_date: date
) -> int:
    relevant = sorted(
        [t for t in temps if not t.get("is_discarded") and _to_date(t["date"]) >= after_date],
        key=lambda t: _to_date(t["date"]),
    )
    count = 0
    for t in relevant:
        if t["temp_value"] > coverline:
            count += 1
        else:
            break
    return count


def analyze_cycle(
    temps: list[TemperatureRecord],
    signs: list[FertilitySignsRecord],
    profile_settings: ProfileSettings,
    past_cycle_lengths: list[int],
    cycle_start_date: date,
    cycle_end_date: date | None = None,
) -> CycleInsights:
    unit = profile_settings.temp_unit
    method = profile_settings.interpretation_method

    temp_dicts = [t.model_dump() for t in temps]
    sign_dicts = [s.model_dump() for s in signs]

    ov: OvulationResult = detect_ovulation(temp_dicts, unit=unit, method=method)

    fw = compute_fertile_window(
        cycle_start_date=cycle_start_date,
        ovulation_result=ov,
        fertility_signs=sign_dicts,
        past_cycle_lengths=past_cycle_lengths,
        unit=unit,
    )

    luteal_length: int | None = None
    if ov.ovulation_date and cycle_end_date:
        luteal_length = max(0, (cycle_end_date - ov.ovulation_date).days)

    consecutive = 0
    if ov.shift_start_date and ov.coverline:
        consecutive = _count_consecutive_elevated(
            temp_dicts, ov.coverline, ov.shift_start_date
        )

    pregnancy_indicator = consecutive >= 18
    short_luteal = luteal_length is not None and luteal_length < 10

    return CycleInsights(
        coverline=ov.coverline,
        ovulation_date=ov.ovulation_date,
        ovulation_confirmed=ov.detected,
        ovulation_confidence=ov.confidence,
        ovulation_method=ov.method,
        fertile_start_date=fw.fertile_start,
        fertile_end_date=fw.fertile_end,
        post_ovulatory_infertile_date=fw.post_ovulatory_infertile,
        luteal_length=luteal_length,
        luteal_phase_short=short_luteal,
        pregnancy_indicator=pregnancy_indicator,
        consecutive_elevated_temps=consecutive,
        engine_version="1.0.0",
    )
