from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


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
    updated_at: datetime | None

    model_config = {"from_attributes": True}


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
    time_taken: time | None
    is_discarded: bool
    discard_reason: str
    notes: str

    model_config = {"from_attributes": True}


class SignsResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    date: date
    menstrual_flow: str
    cervical_mucus: str
    cervical_position: str
    cervical_firmness: str
    cervical_opening: str
    opk_result: str
    notes: str

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


class InsightsResponse(BaseModel):
    id: UUID
    cycle_id: UUID
    coverline: float | None
    ovulation_date: date | None
    ovulation_confirmed: bool
    ovulation_method: str
    fertile_start_date: date | None
    fertile_end_date: date | None
    post_ovulatory_infertile_date: date | None
    luteal_length: int | None
    luteal_phase_short: bool
    pregnancy_indicator: bool
    consecutive_elevated_temps: int
    engine_version: str
    computed_at: datetime

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
