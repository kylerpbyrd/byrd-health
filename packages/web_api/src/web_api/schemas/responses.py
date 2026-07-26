from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    temp_unit: str
    interpretation_method: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


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


class TempResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    temp_value: float
    time_taken: time | None = None
    is_discarded: bool
    discard_reason: str | None = ""
    notes: str | None = ""

    model_config = {"from_attributes": True}


class SignsResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    menstrual_flow: str | None = ""
    cervical_mucus: str | None = ""
    cervical_position: str | None = ""
    cervical_firmness: str | None = ""
    cervical_opening: str | None = ""
    opk_result: str | None = ""
    notes: str | None = ""

    model_config = {"from_attributes": True}


class SymptomResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    symptom_type: str
    severity: int

    model_config = {"from_attributes": True}


class EntryResponse(BaseModel):
    temperature: TempResponse | None = None
    signs: SignsResponse | None = None
    symptoms: list[SymptomResponse] = []


class WarningItem(BaseModel):
    type: str
    message: str


class DashboardResponse(BaseModel):
    phase: str
    cycle_day: int
    avg_cycle_length: int | None = None
    next_period_date: date | None = None
    fertile_start_date: date | None = None
    fertile_end_date: date | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    coverline: float | None = None
    last_temp: float | None = None
    luteal_length: int | None = None
    warnings: list[WarningItem] = []
    today_temp: TempResponse | None = None
    today_signs: SignsResponse | None = None


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


class InsightsDataResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    coverline: float | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    ovulation_confidence: str = "none"
    ovulation_method: str = ""
    fertile_start_date: date | None = None
    fertile_end_date: date | None = None
    post_ovulatory_infertile_date: date | None = None
    luteal_length: int | None = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    consecutive_elevated_temps: int = 0
    engine_version: str = "1.0.0"
    computed_at: datetime | None = None

    model_config = {"from_attributes": True}


class InsightsResponse(BaseModel):
    cycle_day: int
    phase: str
    coverline: float | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    ovulation_confidence: str = "none"
    ovulation_method: str = ""
    fertile_start: date | None = None
    fertile_end: date | None = None
    luteal_length: int | None = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    next_period_date: date | None = None
    avg_cycle_length: int | None = None
    warnings: list[WarningItem] = []
    engine_version: str = "1.0.0"


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
