"""Input validation shared by HTML and JSON write endpoints."""
import re
from datetime import date


FLOW_VALUES = {"", "none", "spotting", "light", "medium", "heavy"}
MUCUS_VALUES = {"", "dry", "sticky", "creamy", "watery", "egg_white"}
OPK_VALUES = {"", "not_tested", "negative", "low", "high", "peak"}
POSITION_VALUES = {"", "low", "mid", "high"}
FIRMNESS_VALUES = {"", "firm", "medium", "soft"}
OPENING_VALUES = {"", "closed", "medium", "open"}
INTERPRETATION_VALUES = {"standard", "conservative"}
SYMPTOM_VALUES = {
    "cramps", "bloating", "breast_tenderness", "ovulation_pain", "headache",
    "spotting", "mood_changes", "fatigue", "other",
}

_TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
_ENTITY_ID_RE = re.compile(r"^[a-z_]+\.[a-z0-9_]+$")


def validate_date(value: str, *, allow_future: bool = False) -> str:
    """Return a normalized ISO date or raise ValueError."""
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must use YYYY-MM-DD format") from exc
    if not allow_future and parsed > date.today():
        raise ValueError("Date cannot be in the future")
    return parsed.isoformat()


def validate_temperature(value, unit: str) -> float:
    """Validate a plausible BBT reading in the profile's configured unit."""
    if unit not in {"F", "C"}:
        raise ValueError("Temperature unit must be F or C")
    try:
        temp = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Temperature must be a numeric value") from exc
    lower, upper = (90.0, 105.0) if unit == "F" else (32.0, 41.0)
    if not lower <= temp <= upper:
        raise ValueError(f"Temperature must be between {lower:g} degrees {unit} and {upper:g} degrees {unit}")
    return temp


def validate_choice(value: str, allowed: set[str], label: str) -> str:
    value = (value or "").strip()
    if value not in allowed:
        raise ValueError(f"Invalid {label}")
    return value


def validate_time(value: str) -> str:
    value = (value or "").strip()
    if value and not _TIME_RE.fullmatch(value):
        raise ValueError("Time must use HH:MM format")
    return value


def validate_profile_name(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError("Profile name is required")
    if len(value) > 80:
        raise ValueError("Profile name must be 80 characters or fewer")
    return value


def validate_entity_id(value: str) -> str:
    value = (value or "").strip()
    if value and not _ENTITY_ID_RE.fullmatch(value):
        raise ValueError("Home Assistant sensor must be a valid entity ID")
    return value
