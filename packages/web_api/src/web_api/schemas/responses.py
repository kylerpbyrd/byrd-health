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
    end_date: Optional[date] = None
    cycle_length: Optional[int] = None
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
    time_taken: Optional[time] = None
    is_discarded: bool
    discard_reason: Optional[str] = ""
    notes: Optional[str] = ""

    model_config = {"from_attributes": True}


class SignsResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    menstrual_flow: Optional[str] = ""
    cervical_mucus: Optional[str] = ""
    cervical_position: Optional[str] = ""
    cervical_firmness: Optional[str] = ""
    cervical_opening: Optional[str] = ""
    opk_result: Optional[str] = ""
    notes: Optional[str] = ""

    model_config = {"from_attributes": True}


class SymptomResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    symptom_type: str
    severity: int

    model_config = {"from_attributes": True}


class EntryResponse(BaseModel):
    temperature: Optional[TempResponse] = None
    signs: Optional[SignsResponse] = None
    symptoms: list[SymptomResponse] = []


class WarningItem(BaseModel):
    type: str
    message: str


class DashboardResponse(BaseModel):
    phase: str
    cycle_day: int
    avg_cycle_length: Optional[int] = None
    next_period_date: Optional[date] = None
    fertile_start_date: Optional[date] = None
    fertile_end_date: Optional[date] = None
    ovulation_date: Optional[date] = None
    ovulation_confirmed: bool = False
    coverline: Optional[float] = None
    last_temp: Optional[float] = None
    luteal_length: Optional[int] = None
    warnings: list[WarningItem] = []
    today_temp: Optional[TempResponse] = None
    today_signs: Optional[SignsResponse] = None


class CycleListItem(BaseModel):
    id: UUID
    start_date: date
    end_date: Optional[date] = None
    cycle_length: Optional[int] = None
    ovulation_date: Optional[date] = None
    ovulation_confirmed: bool = False
    luteal_length: Optional[int] = None
    is_active: bool = False


class CycleListResponse(BaseModel):
    cycles: list[CycleListItem]


class CycleDetailResponse(BaseModel):
    id: UUID
    profile_id: UUID
    start_date: date
    end_date: Optional[date] = None
    cycle_length: Optional[int] = None
    notes: str = ""
    temperatures: list[TempResponse] = []
    signs: list[SignsResponse] = []
    symptoms: list[SymptomResponse] = []
    insights: Optional["InsightsDataResponse"] = None


class InsightsDataResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    coverline: Optional[float] = None
    ovulation_date: Optional[date] = None
    ovulation_confirmed: bool = False
    ovulation_confidence: str = "none"
    ovulation_method: str = ""
    fertile_start_date: Optional[date] = None
    fertile_end_date: Optional[date] = None
    post_ovulatory_infertile_date: Optional[date] = None
    luteal_length: Optional[int] = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    consecutive_elevated_temps: int = 0
    engine_version: str = "1.0.0"
    computed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class InsightsResponse(BaseModel):
    cycle_day: int
    phase: str
    coverline: Optional[float] = None
    ovulation_date: Optional[date] = None
    ovulation_confirmed: bool = False
    ovulation_confidence: str = "none"
    ovulation_method: str = ""
    fertile_start: Optional[date] = None
    fertile_end: Optional[date] = None
    luteal_length: Optional[int] = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    next_period_date: Optional[date] = None
    avg_cycle_length: Optional[int] = None
    warnings: list[WarningItem] = []
    engine_version: str = "1.0.0"


class ChartDataResponse(BaseModel):
    labels: list[str]
    temperatures: list[Optional[float]]
    discarded: list[dict[str, object]]
    coverline: Optional[float] = None
    fertile_start_day: Optional[int] = None
    fertile_end_day: Optional[int] = None
    ovulation_day: Optional[int] = None
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
    cycle_day: Optional[int] = None
    phase: Optional[str] = None
    temp: Optional[float] = None
    flow: Optional[str] = None
    mucus: Optional[str] = None
    opk: Optional[str] = None
    is_period_start: bool = False
    is_ovulation_day: bool = False
    is_fertile: bool = False
    is_today: bool = False
    has_entry: bool = False
    in_current_month: bool = False


class CalendarCycleItem(BaseModel):
    id: UUID
    start_date: date
    end_date: Optional[date] = None
    phase_dates: dict[str, list[str]] = {}


class CalendarProfileInfo(BaseModel):
    slug: str
    temp_unit: str


class CalendarResponse(BaseModel):
    month: str
    profile: CalendarProfileInfo
    days: list[CalendarDayItem]
    cycles_in_range: list[CalendarCycleItem]
