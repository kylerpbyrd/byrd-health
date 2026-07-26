from uuid import UUID

from fastapi import APIRouter, Depends

from fertility_engine import get_current_cycle_day, get_cycle_phase, predict_next_period
from fertility_engine.models import FertileWindowResult

from data_service.models import Profile
from data_service.service import DataService

from ..analysis import run_cycle_analysis, enrich_insights_for_publishing
from ..dependencies import get_active_profile, get_data_service
from ..schemas.responses import InsightsResponse, WarningItem

router = APIRouter(
    prefix="/api/v1/fertility/insights",
    tags=["insights"],
)


async def _build_insights_response(
    data_svc: DataService, profile_id: UUID
) -> InsightsResponse:
    profile = await data_svc.profiles.get_by_id(profile_id)
    cycle = await data_svc.cycles.get_or_create_current(profile_id)
    insights = await data_svc.get_insights(cycle.id)
    past_lengths = await data_svc.cycles.get_past_lengths(profile_id)

    cycle_day = get_current_cycle_day(cycle.start_date)
    avg_cycle_length = (
        round(sum(past_lengths) / len(past_lengths)) if past_lengths else None
    )

    signs = await data_svc.entries_for(profile_id).get_signs_for_cycle(cycle.id)
    flow_days = [
        s.date.isoformat()
        for s in signs
        if s.menstrual_flow in {"spotting", "light", "medium", "heavy"}
    ]

    ins = insights or {}
    fw = FertileWindowResult(
        fertile_start=ins.get("fertile_start_date"),
        fertile_end=ins.get("fertile_end_date"),
        post_ovulatory_infertile=ins.get("post_ovulatory_infertile_date"),
        calendar_rule_day=8,
        mucus_triggered=False,
    )

    phase = get_cycle_phase(
        current_date=__import__("datetime").date.today(),
        cycle_start=cycle.start_date,
        flow_days=flow_days,
        fertile_window=fw,
        ovulation_date=ins.get("ovulation_date"),
        ovulation_confirmed=ins.get("ovulation_confirmed", False),
        post_ov_infertile=ins.get("post_ovulatory_infertile_date"),
    )

    next_period = None
    ovulation_date = ins.get("ovulation_date")
    ovulation_confirmed = ins.get("ovulation_confirmed", False)
    if avg_cycle_length:
        avg_luteal = ins.get("luteal_length") or 14
        next_period = predict_next_period(
            cycle_start_date=cycle.start_date,
            ovulation_date=ovulation_date,
            ovulation_confirmed=ovulation_confirmed,
            average_luteal_length=avg_luteal,
            average_cycle_length=avg_cycle_length,
        )

    warnings = []
    if ins.get("luteal_phase_short"):
        warnings.append(
            WarningItem(
                type="warning",
                message="Short luteal phase detected (< 10 days). Consider consulting a healthcare provider.",
            )
        )
    if ins.get("pregnancy_indicator"):
        warnings.append(
            WarningItem(
                type="info",
                message="18+ consecutive elevated temperatures detected — this may indicate pregnancy!",
            )
        )

    return InsightsResponse(
        cycle_day=cycle_day,
        phase=phase,
        coverline=ins.get("coverline"),
        ovulation_date=ovulation_date,
        ovulation_confirmed=ovulation_confirmed,
        ovulation_confidence=ins.get("ovulation_confidence", "none"),
        ovulation_method=ins.get("ovulation_method", ""),
        fertile_start=ins.get("fertile_start_date"),
        fertile_end=ins.get("fertile_end_date"),
        luteal_length=ins.get("luteal_length"),
        luteal_phase_short=ins.get("luteal_phase_short", False),
        pregnancy_indicator=ins.get("pregnancy_indicator", False),
        next_period_date=next_period,
        avg_cycle_length=avg_cycle_length,
        warnings=warnings,
        engine_version=ins.get("engine_version", "1.0.0"),
    )


@router.get("/", response_model=InsightsResponse)
async def get_insights(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> InsightsResponse:
    return await _build_insights_response(data_svc, profile.id)


@router.post("/reanalyze", response_model=InsightsResponse)
async def reanalyze_insights(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> InsightsResponse:
    cycle = await data_svc.cycles.get_or_create_current(profile.id)
    insights_result = await run_cycle_analysis(
        data_svc=data_svc,
        cycle_id=cycle.id,
        profile_id=profile.id,
        cycle_start_date=cycle.start_date,
        cycle_end_date=cycle.end_date,
    )

    try:
        from ..dependencies import get_ha_bridge
        bridge = get_ha_bridge()
        if bridge:
            enriched = await enrich_insights_for_publishing(
                data_svc, cycle.id, profile.id, insights_result
            )
            await bridge.publish_insights(
                slug=profile.slug,
                name=profile.name,
                temp_unit=profile.temp_unit,
                insights=enriched,
                next_period=enriched.get("next_period_date"),
            )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Failed to publish HA entities", exc_info=True)

    return await _build_insights_response(data_svc, profile.id)
