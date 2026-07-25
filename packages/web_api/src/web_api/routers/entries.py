from datetime import date, time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from data_service.models import Profile
from data_service.service import DataService

from ..analysis import run_cycle_analysis
from ..dependencies import get_active_profile, get_data_service
from ..schemas.responses import EntryResponse, SignsResponse, SymptomResponse, TempResponse

router = APIRouter(
    prefix="/api/v1/fertility/entries",
    tags=["entries"],
)

_F_TEMP_MIN = 90.0
_F_TEMP_MAX = 105.0
_C_TEMP_MIN = 32.0
_C_TEMP_MAX = 41.0


class SymptomItem(BaseModel):
    symptom_type: str
    severity: int = Field(default=1, ge=1, le=3)


class EntryRequest(BaseModel):
    date: date
    temp_value: Optional[float] = None
    time_taken: Optional[time] = None
    is_discarded: bool = False
    discard_reason: str = ""
    menstrual_flow: str = ""
    cervical_mucus: str = ""
    cervical_position: str = ""
    cervical_firmness: str = ""
    cervical_opening: str = ""
    opk_result: str = ""
    symptoms: list[SymptomItem] = []
    is_period_start: bool = False
    notes: str = ""


@router.post("/", response_model=EntryResponse, status_code=201)
async def create_entry(
    entry: EntryRequest,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> EntryResponse:
    if entry.temp_value is not None:
        unit = profile.temp_unit
        if unit == "F" and not (_F_TEMP_MIN <= entry.temp_value <= _F_TEMP_MAX):
            raise HTTPException(
                status_code=422,
                detail=f"Temperature must be between {_F_TEMP_MIN} °F and {_F_TEMP_MAX} °F",
            )
        elif unit == "C" and not (_C_TEMP_MIN <= entry.temp_value <= _C_TEMP_MAX):
            raise HTTPException(
                status_code=422,
                detail=f"Temperature must be between {_C_TEMP_MIN} °C and {_C_TEMP_MAX} °C",
            )

    if entry.is_period_start:
        current_cycle = await data_svc.cycles.get_or_create_current(profile.id)
        if entry.date > current_cycle.start_date:
            import datetime as dt

            prev_end = entry.date - dt.timedelta(days=1)
            await data_svc.cycles.close_cycle(
                current_cycle.id, prev_end, profile.id
            )
            await data_svc.cycles.create(profile.id, entry.date)
            await data_svc.session.commit()

    cycle = await data_svc.cycles.get_or_create_current(profile.id)

    if entry.date < cycle.start_date:
        raise HTTPException(
            status_code=400,
            detail="Entry date cannot be before the current cycle start",
        )

    entries = data_svc.entries_for(profile.id)

    temp = None
    if entry.temp_value is not None:
        temp = await entries.upsert_temperature(
            cycle_id=cycle.id,
            entry_date=entry.date,
            temp_value=entry.temp_value,
            time_taken=entry.time_taken,
            is_discarded=entry.is_discarded,
            discard_reason=entry.discard_reason,
            notes=entry.notes,
        )

    signs = None
    has_signs = any(
        [
            entry.menstrual_flow,
            entry.cervical_mucus,
            entry.cervical_position,
            entry.cervical_firmness,
            entry.cervical_opening,
            entry.opk_result,
            entry.notes,
        ]
    )
    if has_signs:
        signs = await entries.upsert_signs(
            cycle_id=cycle.id,
            entry_date=entry.date,
            menstrual_flow=entry.menstrual_flow,
            cervical_mucus=entry.cervical_mucus,
            cervical_position=entry.cervical_position,
            cervical_firmness=entry.cervical_firmness,
            cervical_opening=entry.cervical_opening,
            opk_result=entry.opk_result,
            notes=entry.notes,
        )

    symptoms = []
    if entry.symptoms:
        symptom_dicts = [
            {"symptom_type": s.symptom_type, "severity": s.severity}
            for s in entry.symptoms
        ]
        symptoms = await entries.upsert_symptoms(
            cycle_id=cycle.id,
            entry_date=entry.date,
            symptoms=symptom_dicts,
        )

    await data_svc.session.commit()

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
            await bridge.publish_insights(
                slug=profile.slug,
                name=profile.name,
                temp_unit=profile.temp_unit,
                insights=insights_result,
                next_period=insights_result.get("next_period_date"),
            )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Failed to publish HA entities", exc_info=True)

    return EntryResponse(
        temperature=TempResponse.model_validate(temp) if temp else None,
        signs=SignsResponse.model_validate(signs) if signs else None,
        symptoms=[SymptomResponse.model_validate(s) for s in symptoms],
    )


@router.get("/today", response_model=EntryResponse)
async def get_today_entry(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> EntryResponse:
    from datetime import date as date_type

    cycle = await data_svc.cycles.get_or_create_current(profile.id)
    today = date_type.today()

    entries = data_svc.entries_for(profile.id)

    temp = await entries.get_temperature(cycle.id, today)
    signs = await entries.get_signs(cycle.id, today)

    symptoms_list = await entries.get_symptoms_for_cycle(cycle.id)
    today_symptoms = [s for s in symptoms_list if s.date == today]

    return EntryResponse(
        temperature=TempResponse.model_validate(temp) if temp else None,
        signs=SignsResponse.model_validate(signs) if signs else None,
        symptoms=[SymptomResponse.model_validate(s) for s in today_symptoms],
    )
