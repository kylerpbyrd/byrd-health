from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from data_service.schemas import (
    EntryResponse,
    InsightsResponse,
    ProfileResponse,
    SignsResponse,
    SymptomResponse,
    TempResponse,
    WarningItem,
)

InsightsDataResponse = InsightsResponse


class ProfileExportResponse(BaseModel):
    profile: ProfileResponse
    cycles: list["CycleExportItem"]

    model_config = {"from_attributes": True}


class CycleExportItem(BaseModel):
    id: UUID
    start_date: date
    end_date: date | None = None
    cycle_length: int | None = None
    notes: str = ""
    temperatures: list["TempResponse"]
    fertility_signs: list["SignsResponse"]
    symptoms: list["SymptomResponse"]
    insights: Optional["InsightsDataResponse"] = None


class CycleListItem(BaseModel):
    id: UUID
    start_date: date
    end_date: date | None = None
    cycle_length: int | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    luteal_length: int | None = None
    is_active: bool = False


class CycleListResponse(BaseModel):
    cycles: list[CycleListItem]


class CycleDetailResponse(BaseModel):
    id: UUID
    profile_id: UUID
    start_date: date
    end_date: date | None = None
    cycle_length: int | None = None
    notes: str = ""
    temperatures: list[TempResponse] = []
    signs: list[SignsResponse] = []
    symptoms: list[SymptomResponse] = []
    insights: Optional["InsightsDataResponse"] = None


class ChartDataResponse(BaseModel):
    labels: list[str]
    temperatures: list[float | None]
    discarded: list[dict[str, object]]
    coverline: float | None = None
    fertile_start_day: int | None = None
    fertile_end_day: int | None = None
    ovulation_day: int | None = None
    mucus: dict[str, str]
    opk: dict[str, str]
    unit: str


class ExportResponse(BaseModel):
    format: str = "byrd-health-export"
    version: int = 1
    exported_at: str
    profile: ProfileResponse
    cycles: list[CycleExportItem]


class CalendarDayItem(BaseModel):
    date: str
    cycle_day: int | None = None
    phase: str | None = None
    temp: float | None = None
    flow: str | None = None
    mucus: str | None = None
    opk: str | None = None
    is_period_start: bool = False
    is_ovulation_day: bool = False
    is_fertile: bool = False
    is_today: bool = False
    has_entry: bool = False
    in_current_month: bool = False


class CalendarCycleItem(BaseModel):
    id: UUID
    start_date: date
    end_date: date | None = None
    phase_dates: dict[str, list[str]] = {}


class CalendarProfileInfo(BaseModel):
    slug: str
    temp_unit: str


class CalendarResponse(BaseModel):
    month: str
    profile: CalendarProfileInfo
    days: list[CalendarDayItem]
    cycles_in_range: list[CalendarCycleItem]
