from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ProfileCreate(BaseModel):
    name: str = Field(max_length=80)
    temp_unit: str = Field(default="F", max_length=1)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    temp_unit: str | None = Field(default=None, max_length=1)
    interpretation_method: str | None = Field(default=None, max_length=16)


class ProfileResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    temp_unit: str
    interpretation_method: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _safe_from_orm(cls, data: Any) -> Any:
        if isinstance(data, dict) or not hasattr(data, "__dict__"):
            return data
        result: dict[str, Any] = {}
        for field_name in cls.model_fields:
            try:
                result[field_name] = getattr(data, field_name)
            except Exception:
                pass
        return result


class CycleCreate(BaseModel):
    start_date: date


class CycleResponse(BaseModel):
    id: UUID
    profile_id: UUID
    start_date: date
    end_date: date | None
    cycle_length: int | None
    notes: str

    model_config = {"from_attributes": True}


class EntryCreate(BaseModel):
    temp_value: float | None = None
    date: date
    time_taken: time | None = None
    signs: dict[str, str] | None = None
    symptoms: list[dict[str, str | int]] | None = None
    is_period_start: bool = False


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

    model_config = {"from_attributes": True}


class WarningItem(BaseModel):
    type: str
    message: str


class InsightsResponse(BaseModel):
    id: UUID | None = None
    cycle_id: UUID | None = None
    coverline: float | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
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
    cycle_day: int = 1
    phase: str = "pre_ovulatory"
    ovulation_confidence: str = "none"
    fertile_start: date | None = None
    fertile_end: date | None = None
    next_period_date: date | None = None
    avg_cycle_length: int | None = None
    warnings: list[WarningItem] = []

    model_config = {"from_attributes": True}


class ExportResponse(BaseModel):
    profile: ProfileResponse
    cycles: list["ExportCycle"]


class ExportCycle(BaseModel):
    id: UUID
    start_date: date
    end_date: date | None
    cycle_length: int | None
    notes: str
    temperatures: list[TempResponse]
    fertility_signs: list[SignsResponse]
    symptoms: list[SymptomResponse]
    insights: InsightsResponse | None

    model_config = {"from_attributes": True}
