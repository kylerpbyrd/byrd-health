from datetime import date
from typing import Any, Literal, Optional, cast
from uuid import UUID

from fertility_engine import (
    FertilitySignsRecord,
    ProfileSettings,
    TemperatureRecord,
    analyze_cycle,
)
from data_service.service import DataService


async def run_cycle_analysis(
    data_svc: DataService,
    cycle_id: UUID,
    profile_id: UUID,
    cycle_start_date: date,
    cycle_end_date: Optional[date] = None,
) -> dict[str, Any]:
    temps = await data_svc.entries.get_temps_for_cycle(cycle_id)
    signs = await data_svc.entries.get_signs_for_cycle(cycle_id)
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
