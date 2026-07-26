import calendar as cal_module
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from data_service.models import Profile
from data_service.service import DataService
from fertility_engine import get_cycle_phase, FertileWindowResult

from ..dependencies import get_active_profile, get_data_service
from ..schemas.responses import CalendarResponse, CalendarDayItem, CalendarCycleItem

router = APIRouter(
    prefix="/api/v1/fertility/calendar",
    tags=["calendar"],
)


def _parse_month(month_str: str) -> tuple[int, int]:
    try:
        y, m = month_str.split("-")
        return int(y), int(m)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="month must be YYYY-MM format")


def _grid_range(first_of_month: date) -> tuple[date, date]:
    py_weekday = first_of_month.weekday()
    sun_offset = (py_weekday + 1) % 7
    grid_start = first_of_month - timedelta(days=sun_offset)
    grid_end = grid_start + timedelta(days=41)
    return grid_start, grid_end


_PHASE_MAP = {"pre_ovulatory": "follicular"}


def _export_phase(engine_phase: str) -> str:
    return _PHASE_MAP.get(engine_phase, engine_phase)


@router.get("/", response_model=CalendarResponse)
async def get_calendar(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    profile_id: Optional[UUID] = Query(None),
    data_svc: DataService = Depends(get_data_service),
    active_profile: Profile = Depends(get_active_profile),
) -> CalendarResponse:
    if profile_id:
        profile = await data_svc.profiles.get_by_id(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
    else:
        profile = active_profile

    year, month_num = _parse_month(month)
    first_of_month = date(year, month_num, 1)
    grid_start, grid_end = _grid_range(first_of_month)
    today = date.today()

    all_cycles = await data_svc.cycles.get_by_profile(profile.id)
    entries_repo = data_svc.entries_for(profile.id)

    overlapping: list[tuple] = []
    for cycle in all_cycles:
        c_end = cycle.end_date or today + timedelta(days=365)
        if cycle.start_date <= grid_end and c_end >= grid_start:
            overlapping.append(cycle)

    cycle_data_map: dict[UUID, dict] = {}
    for cycle in overlapping:
        insights = await data_svc.get_insights(cycle.id)
        signs = await entries_repo.get_signs_for_cycle(cycle.id)
        temps_for_cycle = await entries_repo.get_temps_for_cycle(cycle.id)

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

        phase_map: dict[date, str] = {}
        c_start = cycle.start_date
        c_end = cycle.end_date or (grid_end + timedelta(days=365))

        current = max(c_start, grid_start)
        while current <= min(c_end, grid_end):
            ph = get_cycle_phase(
                current_date=current,
                cycle_start=c_start,
                flow_days=flow_days,
                fertile_window=fw,
                ovulation_date=ins.get("ovulation_date"),
                ovulation_confirmed=ins.get("ovulation_confirmed", False),
                post_ov_infertile=ins.get("post_ovulatory_infertile_date"),
            )
            phase_map[current] = _export_phase(ph)
            current += timedelta(days=1)

        temp_map: dict[date, float] = {}
        for t in temps_for_cycle:
            if not t.is_discarded and grid_start <= t.date <= grid_end:
                temp_map[t.date] = t.temp_value

        sign_map: dict[date, dict[str, Optional[str]]] = {}
        for s in signs:
            if grid_start <= s.date <= grid_end:
                sign_map[s.date] = {
                    "flow": s.menstrual_flow or None,
                    "mucus": s.cervical_mucus or None,
                    "opk": s.opk_result or None,
                }

        cycle_data_map[cycle.id] = {
            "cycle": cycle,
            "phase_map": phase_map,
            "temp_map": temp_map,
            "sign_map": sign_map,
            "insights": ins,
            "signs": signs,
        }

    days: list[CalendarDayItem] = []
    current = grid_start
    while current <= grid_end:
        in_current_month = current.month == month_num and current.year == year

        found_cycle_id: Optional[UUID] = None
        for c_id, c_data in cycle_data_map.items():
            c_obj = c_data["cycle"]
            c_end = c_obj.end_date or date(2099, 12, 31)
            if c_obj.start_date <= current <= c_end:
                found_cycle_id = c_id
                break

        cycle_day: Optional[int] = None
        phase: Optional[str] = None
        temp: Optional[float] = None
        flow: Optional[str] = None
        mucus: Optional[str] = None
        opk: Optional[str] = None
        is_period_start = False
        is_ovulation_day = False
        is_fertile = False
        has_entry = False

        if found_cycle_id:
            c_data = cycle_data_map[found_cycle_id]
            cycle_obj = c_data["cycle"]
            cycle_day = (current - cycle_obj.start_date).days + 1

            if current in c_data["phase_map"]:
                ph = c_data["phase_map"][current]
                phase = ph
                if ph == "fertile":
                    is_fertile = True

            if current in c_data["temp_map"]:
                temp = c_data["temp_map"][current]
                has_entry = True

            if current in c_data["sign_map"]:
                signs_data = c_data["sign_map"][current]
                flow = signs_data["flow"]
                mucus = signs_data["mucus"]
                opk = signs_data["opk"]
                if flow:
                    has_entry = True
                if mucus:
                    has_entry = True
                if opk:
                    has_entry = True

            if cycle_obj.start_date == current:
                is_period_start = True

            ins = c_data["insights"]
            ov_date = ins.get("ovulation_date")
            if ov_date == current:
                is_ovulation_day = True

        days.append(CalendarDayItem(
            date=current.isoformat(),
            cycle_day=cycle_day,
            phase=phase,
            temp=temp,
            flow=flow,
            mucus=mucus,
            opk=opk,
            is_period_start=is_period_start,
            is_ovulation_day=is_ovulation_day,
            is_fertile=is_fertile,
            is_today=current == today,
            has_entry=has_entry,
            in_current_month=in_current_month,
        ))

        current += timedelta(days=1)

    phase_order = ["menstruation", "follicular", "fertile", "luteal"]

    cycles_in_range: list[CalendarCycleItem] = []
    for c_data in cycle_data_map.values():
        cycle_obj = c_data["cycle"]
        phase_dates: dict[str, list[str]] = {}
        for d, ph in c_data["phase_map"].items():
            phase_dates.setdefault(ph, []).append(d.isoformat())

        ordered: dict[str, list[str]] = {}
        for ph in phase_order:
            if ph in phase_dates:
                ordered[ph] = sorted(phase_dates[ph])
        for ph in sorted(phase_dates):
            if ph not in ordered:
                ordered[ph] = sorted(phase_dates[ph])

        cycles_in_range.append(CalendarCycleItem(
            id=cycle_obj.id,
            start_date=cycle_obj.start_date,
            end_date=cycle_obj.end_date,
            phase_dates=ordered,
        ))

    return CalendarResponse(
        month=month,
        profile={
            "slug": profile.slug,
            "temp_unit": profile.temp_unit,
        },
        days=days,
        cycles_in_range=cycles_in_range,
    )
