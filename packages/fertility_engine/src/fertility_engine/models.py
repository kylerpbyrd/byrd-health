from datetime import date
from typing import Literal

from pydantic import BaseModel


class TemperatureRecord(BaseModel):
    date: date
    temp_value: float
    cycle_day: int
    is_discarded: bool = False


class FertilitySignsRecord(BaseModel):
    date: date
    cervical_mucus: str | None = None
    opk_result: str | None = None


class OvulationResult(BaseModel):
    detected: bool
    ovulation_date: date | None = None
    shift_start_date: date | None = None
    coverline: float | None = None
    method: str = "none"
    confidence: Literal["confirmed", "possible", "none"] = "none"
    consecutive_elevated: int = 0


class FertileWindowResult(BaseModel):
    fertile_start: date | None = None
    fertile_end: date | None = None
    post_ovulatory_infertile: date | None = None
    calendar_rule_day: int
    mucus_triggered: bool = False


class CycleInsights(BaseModel):
    coverline: float | None = None
    ovulation_date: date | None = None
    ovulation_confirmed: bool = False
    ovulation_confidence: Literal["confirmed", "possible", "none"] = "none"
    ovulation_method: str = "none"
    fertile_start_date: date | None = None
    fertile_end_date: date | None = None
    post_ovulatory_infertile_date: date | None = None
    luteal_length: int | None = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    consecutive_elevated_temps: int = 0
    engine_version: str = "1.0.0"


class ProfileSettings(BaseModel):
    temp_unit: Literal["F", "C"] = "F"
    interpretation_method: Literal["standard", "conservative"] = "standard"
