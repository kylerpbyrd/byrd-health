from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from data_service.models import Profile
from data_service.service import DataService

from ..dependencies import get_active_profile, get_data_service
from ..schemas.responses import (
    ChartDataResponse,
    CycleDetailResponse,
    CycleListItem,
    CycleListResponse,
    InsightsDataResponse,
    SignsResponse,
    SymptomResponse,
    TempResponse,
)

router = APIRouter(
    prefix="/api/v1/fertility/cycles",
    tags=["cycles"],
)


class NewCycleRequest(BaseModel):
    start_date: date


@router.get("/", response_model=CycleListResponse)
async def list_cycles(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> CycleListResponse:
    await data_svc.cycles.get_or_create_current(profile.id)
    await data_svc.session.commit()
    cycles = await data_svc.cycles.get_by_profile(profile.id)
    items = []
    for c in cycles:
        insights = await data_svc.get_insights(c.id)
        is_active = c.end_date is None
        item = CycleListItem(
            id=c.id,
            start_date=c.start_date,
            end_date=c.end_date,
            cycle_length=c.cycle_length,
            ovulation_date=insights.get("ovulation_date") if insights else None,
            ovulation_confirmed=(
                insights.get("ovulation_confirmed", False) if insights else False
            ),
            luteal_length=insights.get("luteal_length") if insights else None,
            is_active=is_active,
        )
        items.append(item)
    return CycleListResponse(cycles=items)


@router.get("/current", response_model=CycleDetailResponse)
async def get_current_cycle(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> CycleDetailResponse:
    cycle = await data_svc.cycles.get_or_create_current(profile.id)
    return await _build_cycle_detail(data_svc, cycle.id, profile.id)


@router.get("/{cycle_id}", response_model=CycleDetailResponse)
async def get_cycle(
    cycle_id: UUID,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> CycleDetailResponse:
    cycle = await data_svc.cycles.get_by_id(cycle_id, profile.id)
    if cycle is None:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return await _build_cycle_detail(data_svc, cycle_id, profile.id)


@router.get("/{cycle_id}/chart", response_model=ChartDataResponse)
async def get_cycle_chart(
    cycle_id: UUID,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> ChartDataResponse:
    cycle = await data_svc.cycles.get_by_id(cycle_id, profile.id)
    if cycle is None:
        raise HTTPException(status_code=404, detail="Cycle not found")

    temps = await data_svc.entries.get_temps_for_cycle(cycle_id)
    signs_list = await data_svc.entries.get_signs_for_cycle(cycle_id)
    insights = await data_svc.get_insights(cycle_id)

    labels = []
    temperatures: list[float | None] = []
    discarded = []

    for t in temps:
        cycle_day = (t.date - cycle.start_date).days + 1
        label = f"Day {cycle_day}"
        labels.append(label)
        if t.is_discarded:
            temperatures.append(None)
            discarded.append({"x": label, "y": t.temp_value})
        else:
            temperatures.append(t.temp_value)

    mucus_map: dict[str, str] = {}
    opk_map: dict[str, str] = {}
    for s in signs_list:
        if s.cervical_mucus:
            day_num = (s.date - cycle.start_date).days + 1
            mucus_map[str(day_num)] = s.cervical_mucus
        if s.opk_result:
            day_num = (s.date - cycle.start_date).days + 1
            opk_map[str(day_num)] = s.opk_result

    result = ChartDataResponse(
        labels=labels,
        temperatures=temperatures,
        discarded=discarded,
        coverline=None,
        fertile_start_day=None,
        fertile_end_day=None,
        ovulation_day=None,
        mucus=mucus_map,
        opk=opk_map,
        unit=profile.temp_unit,
    )

    if insights:
        result.coverline = insights.get("coverline")
        for insight_key, chart_key in [
            ("fertile_start_date", "fertile_start_day"),
            ("fertile_end_date", "fertile_end_day"),
            ("ovulation_date", "ovulation_day"),
        ]:
            val = insights.get(insight_key)
            if val:
                if isinstance(val, str):
                    val = date.fromisoformat(val)
                day = (val - cycle.start_date).days + 1
                setattr(result, chart_key, day)

    return result


@router.post("/", response_model=CycleDetailResponse, status_code=201)
async def start_new_cycle(
    body: NewCycleRequest,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> CycleDetailResponse:
    current_cycle = await data_svc.cycles.get_or_create_current(profile.id)
    if body.start_date <= current_cycle.start_date:
        raise HTTPException(
            status_code=400,
            detail="New cycle start must be after the current cycle start.",
        )

    prev_end = body.start_date - __import__("datetime").timedelta(days=1)
    await data_svc.cycles.close_cycle(current_cycle.id, prev_end, profile.id)
    new_cycle = await data_svc.cycles.create(profile.id, body.start_date)
    await data_svc.session.commit()

    return await _build_cycle_detail(data_svc, new_cycle.id, profile.id)


async def _build_cycle_detail(
    data_svc: DataService, cycle_id: UUID, profile_id: UUID
) -> CycleDetailResponse:
    cycle = await data_svc.cycles.get_by_id(cycle_id, profile_id)
    if cycle is None:
        raise HTTPException(status_code=404, detail="Cycle not found")

    temps = await data_svc.entries.get_temps_for_cycle(cycle_id)
    signs = await data_svc.entries.get_signs_for_cycle(cycle_id)
    symptoms = await data_svc.entries.get_symptoms_for_cycle(cycle_id)
    insights = await data_svc.get_insights(cycle_id)

    return CycleDetailResponse(
        id=cycle.id,
        profile_id=cycle.profile_id,
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        cycle_length=cycle.cycle_length,
        notes=cycle.notes,
        temperatures=[TempResponse.model_validate(t) for t in temps],
        signs=[SignsResponse.model_validate(s) for s in signs],
        symptoms=[SymptomResponse.model_validate(s) for s in symptoms],
        insights=(
            InsightsDataResponse(
                id=insights["id"],
                cycle_id=insights["cycle_id"],
                coverline=insights.get("coverline"),
                ovulation_date=insights.get("ovulation_date"),
                ovulation_confirmed=insights.get("ovulation_confirmed", False),
                ovulation_confidence=insights.get("ovulation_confidence", "none"),
                ovulation_method=insights.get("ovulation_method", ""),
                fertile_start_date=insights.get("fertile_start_date"),
                fertile_end_date=insights.get("fertile_end_date"),
                post_ovulatory_infertile_date=insights.get(
                    "post_ovulatory_infertile_date"
                ),
                luteal_length=insights.get("luteal_length"),
                luteal_phase_short=insights.get("luteal_phase_short", False),
                pregnancy_indicator=insights.get("pregnancy_indicator", False),
                consecutive_elevated_temps=insights.get(
                    "consecutive_elevated_temps", 0
                ),
                engine_version=insights.get("engine_version", "1.0.0"),
                computed_at=insights.get("computed_at"),
            )
            if insights
            else None
        ),
    )
