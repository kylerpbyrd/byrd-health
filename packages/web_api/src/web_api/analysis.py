from datetime import date
from datetime import datetime as dt
from typing import Any, Literal, cast
from uuid import UUID

from data_service.service import DataService
from fertility_engine import (
    FertilitySignsRecord,
    ProfileSettings,
    TemperatureRecord,
    analyze_cycle,
    get_current_cycle_day,
    get_cycle_phase,
    predict_next_period,
)
from fertility_engine.models import FertileWindowResult


async def run_cycle_analysis(
    data_svc: DataService,
    cycle_id: UUID,
    profile_id: UUID,
    cycle_start_date: date,
    cycle_end_date: date | None = None,
) -> dict[str, Any]:
    entries = data_svc.entries_for(profile_id)
    temps = await entries.get_temps_for_cycle(cycle_id)
    signs = await entries.get_signs_for_cycle(cycle_id)
    profile = await data_svc.profiles.get_by_id(profile_id)
    past_lengths = await data_svc.cycles.get_past_lengths(profile_id)

    temp_records = [
        TemperatureRecord(
            date=t.date,
            temp_value=t.temp_value,
            cycle_day=(t.date - cycle_start_date).days + 1,
            is_discarded=t.is_discarded,
        )
        for t in temps
    ]

    sign_records: list[FertilitySignsRecord] = []
    for s in signs:
        if s.cervical_mucus or s.opk_result:
            sign_records.append(
                FertilitySignsRecord(
                    date=s.date,
                    cervical_mucus=s.cervical_mucus,
                    opk_result=s.opk_result,
                )
            )

    profile_settings = ProfileSettings(
        temp_unit=cast(Literal["F", "C"], profile.temp_unit if profile else "F"),
        interpretation_method=cast(
            Literal["standard", "conservative"],
            profile.interpretation_method if profile else "standard",
        ),
    )

    insights = analyze_cycle(
        temps=temp_records,
        signs=sign_records,
        profile_settings=profile_settings,
        past_cycle_lengths=past_lengths,
        cycle_start_date=cycle_start_date,
        cycle_end_date=cycle_end_date,
    )

    insights_dict = insights.model_dump()
    insights_dict.pop("ovulation_confidence", None)
    await data_svc.save_insights(cycle_id, insights_dict)
    await data_svc.session.commit()

    return insights.model_dump()


async def enrich_insights_for_publishing(
    data_svc: DataService,
    cycle_id: UUID,
    profile_id: UUID,
    insights_result: dict[str, Any],
) -> dict[str, Any]:
    cycle = await data_svc.cycles.get_by_id(cycle_id)
    if not cycle:
        return insights_result

    past_lengths = await data_svc.cycles.get_past_lengths(profile_id)

    cycle_day = get_current_cycle_day(cycle.start_date)
    avg_cycle_length = (
        round(sum(past_lengths) / len(past_lengths)) if past_lengths else None
    )

    entries = data_svc.entries_for(profile_id)
    signs = await entries.get_signs_for_cycle(cycle_id)
    flow_days = [
        s.date.isoformat()
        for s in signs
        if s.menstrual_flow in {"spotting", "light", "medium", "heavy"}
    ]

    fw = FertileWindowResult(
        fertile_start=insights_result.get("fertile_start_date"),
        fertile_end=insights_result.get("fertile_end_date"),
        post_ovulatory_infertile=insights_result.get("post_ovulatory_infertile_date"),
        calendar_rule_day=8,
        mucus_triggered=False,
    )

    phase = get_cycle_phase(
        current_date=date.today(),
        cycle_start=cycle.start_date,
        flow_days=flow_days,
        fertile_window=fw,
        ovulation_date=insights_result.get("ovulation_date"),
        ovulation_confirmed=insights_result.get("ovulation_confirmed", False),
        post_ov_infertile=insights_result.get("post_ovulatory_infertile_date"),
    )

    temps = await entries.get_temps_for_cycle(cycle_id)
    last_temp = None
    for t in reversed(temps):
        if not t.is_discarded:
            last_temp = t.temp_value
            break

    next_period = None
    ovulation_date = insights_result.get("ovulation_date")
    ovulation_confirmed = insights_result.get("ovulation_confirmed", False)
    if avg_cycle_length:
        avg_luteal = insights_result.get("luteal_length") or 14
        next_period = predict_next_period(
            cycle_start_date=cycle.start_date,
            ovulation_date=ovulation_date,
            ovulation_confirmed=ovulation_confirmed,
            average_luteal_length=avg_luteal,
            average_cycle_length=avg_cycle_length,
        )

    enriched = dict(insights_result)
    enriched["cycle_day"] = cycle_day
    enriched["phase"] = phase
    enriched["last_temp"] = last_temp
    enriched["avg_cycle_length"] = avg_cycle_length
    enriched["next_period_date"] = (
        next_period.isoformat() if isinstance(next_period, date) else None
    )

    return enriched
