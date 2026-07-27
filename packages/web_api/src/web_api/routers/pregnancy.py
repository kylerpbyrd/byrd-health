from datetime import date
from uuid import UUID

from data_service.models import Profile
from data_service.schemas import PregnancyCreate, PregnancyResponse, PregnancyUpdate
from data_service.service import DataService
from fastapi import APIRouter, Depends, HTTPException
from pregnancy_engine import (
    calculate_current_week,
    calculate_days_remaining,
    calculate_due_date,
    calculate_trimester,
)
from sqlalchemy import inspect

from ..dependencies import get_active_profile, get_data_service

router = APIRouter(
    prefix="/api/v1/fertility/pregnancy",
    tags=["pregnancy"],
)


def _safe_get(insp, attr: str, obj):
    if attr not in insp.unloaded:
        return getattr(obj, attr)
    return None


def _build_pregnancy_response(pregnancy, applied_date: date | None = None) -> PregnancyResponse:
    ref_date = applied_date or date.today()
    current_week = calculate_current_week(pregnancy.lmp_date, ref_date)
    trimester = calculate_trimester(current_week)
    days_remaining = None
    if pregnancy.due_date:
        days_remaining = calculate_days_remaining(pregnancy.due_date, ref_date)

    insp = inspect(pregnancy)
    created_at = _safe_get(insp, "created_at", pregnancy)
    updated_at = _safe_get(insp, "updated_at", pregnancy)

    return PregnancyResponse(
        id=pregnancy.id,
        cycle_id=pregnancy.cycle_id,
        profile_id=pregnancy.profile_id,
        lmp_date=pregnancy.lmp_date,
        due_date=pregnancy.due_date,
        current_week=current_week,
        trimester=trimester,
        days_remaining=days_remaining,
        is_active=pregnancy.is_active if _safe_get(insp, "is_active", pregnancy) is not None else True,
        notes=_safe_get(insp, "notes", pregnancy),
        created_at=created_at,
        updated_at=updated_at,
    )


@router.post(
    "/",
    response_model=PregnancyResponse,
    status_code=201,
    summary="Start tracking a pregnancy",
)
async def start_pregnancy(
    body: PregnancyCreate,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> PregnancyResponse:
    try:
        cycle_id = UUID(body.cycle_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cycle_id format")

    cycle = await data_svc.cycles.get_by_id(cycle_id, profile_id=profile.id)
    if cycle is None:
        raise HTTPException(status_code=404, detail="Cycle not found or does not belong to active profile")

    existing = await data_svc.pregnancies.get_by_cycle(cycle_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="This cycle already has a pregnancy record")

    lmp_date = date.fromisoformat(body.lmp_date)

    ovulation_date = None
    if body.ovulation_date:
        ovulation_date = date.fromisoformat(body.ovulation_date)

    due_date = calculate_due_date(ovulation_date=ovulation_date, lmp_date=lmp_date)

    pregnancy = await data_svc.pregnancies.create(
        profile_id=profile.id,
        cycle_id=cycle_id,
        lmp_date=lmp_date,
        due_date=due_date,
    )

    current_week = calculate_current_week(lmp_date)
    trimester = calculate_trimester(current_week)

    await data_svc.pregnancies.update(
        pregnancy.id,
        current_week=current_week,
        trimester=trimester,
    )

    pregnancy.current_week = current_week
    pregnancy.trimester = trimester

    await data_svc.session.commit()

    return _build_pregnancy_response(pregnancy)


@router.get(
    "/",
    response_model=PregnancyResponse,
    summary="Get current pregnancy",
)
async def get_pregnancy(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> PregnancyResponse:
    pregnancy = await data_svc.pregnancies.get_active(profile.id)
    if pregnancy is None:
        raise HTTPException(status_code=404, detail="No active pregnancy found")
    return _build_pregnancy_response(pregnancy)


@router.patch(
    "/",
    response_model=PregnancyResponse,
    summary="Update pregnancy",
)
async def update_pregnancy(
    body: PregnancyUpdate,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> PregnancyResponse:
    pregnancy = await data_svc.pregnancies.get_active(profile.id)
    if pregnancy is None:
        raise HTTPException(status_code=404, detail="No active pregnancy found")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    pregnancy = await data_svc.pregnancies.update(pregnancy.id, **update_data)

    await data_svc.session.commit()

    return _build_pregnancy_response(pregnancy)
