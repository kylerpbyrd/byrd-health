from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


class TemperatureRecord(BaseModel):
    date: date
    temp_value: float
    cycle_day: int
    is_discarded: bool = False


class FertilitySignsRecord(BaseModel):
    date: date
    cervical_mucus: Optional[str] = None
    opk_result: Optional[str] = None


class OvulationResult(BaseModel):
    detected: bool
    ovulation_date: Optional[date] = None
    shift_start_date: Optional[date] = None
    coverline: Optional[float] = None
    method: str = "none"
    confidence: Literal["confirmed", "possible", "none"] = "none"
    consecutive_elevated: int = 0


class FertileWindowResult(BaseModel):
    fertile_start: Optional[date] = None
    fertile_end: Optional[date] = None
    post_ovulatory_infertile: Optional[date] = None
    calendar_rule_day: int
    mucus_triggered: bool = False


class CycleInsights(BaseModel):
    coverline: Optional[float] = None
    ovulation_date: Optional[date] = None
    ovulation_confirmed: bool = False
    ovulation_confidence: Literal["confirmed", "possible", "none"] = "none"
    ovulation_method: str = "none"
    fertile_start_date: Optional[date] = None
    fertile_end_date: Optional[date] = None
    post_ovulatory_infertile_date: Optional[date] = None
    luteal_length: Optional[int] = None
    luteal_phase_short: bool = False
    pregnancy_indicator: bool = False
    consecutive_elevated_temps: int = 0
    engine_version: str = "1.0.0"


class ProfileSettings(BaseModel):
    temp_unit: Literal["F", "C"] = "F"
    interpretation_method: Literal["standard", "conservative"] = "standard"
