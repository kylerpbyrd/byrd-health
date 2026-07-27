from datetime import date
from typing import Any


def generate_explanation(
    insights: Any,
    temp_unit: str = "F",
    cycle_start_date: date | None = None,
    temp_count: int | None = None,
) -> str:
    if isinstance(insights, dict):
        coverline = insights.get("coverline")
        ovulation_date = insights.get("ovulation_date")
        ovulation_confirmed = insights.get("ovulation_confirmed", False)
        ovulation_confidence = insights.get("ovulation_confidence", "none")
        ovulation_method = insights.get("ovulation_method", "none")
        fertile_start_date = insights.get("fertile_start_date") or insights.get("fertile_start")
        fertile_end_date = insights.get("fertile_end_date") or insights.get("fertile_end")
        luteal_length = insights.get("luteal_length")
        luteal_phase_short = insights.get("luteal_phase_short", False)
        phase = insights.get("phase", "")
        cycle_day = insights.get("cycle_day")
    else:
        coverline = getattr(insights, "coverline", None)
        ovulation_date = getattr(insights, "ovulation_date", None)
        ovulation_confirmed = getattr(insights, "ovulation_confirmed", False)
        ovulation_confidence = getattr(insights, "ovulation_confidence", "none")
        ovulation_method = getattr(insights, "ovulation_method", "none")
        fertile_start_date = getattr(insights, "fertile_start_date", None) or getattr(insights, "fertile_start", None)
        fertile_end_date = getattr(insights, "fertile_end_date", None) or getattr(insights, "fertile_end", None)
        luteal_length = getattr(insights, "luteal_length", None)
        luteal_phase_short = getattr(insights, "luteal_phase_short", False)
        phase = getattr(insights, "phase", "")
        cycle_day = getattr(insights, "cycle_day", None)

    def _cd(d: Any) -> int | None:
        if d is None or cycle_start_date is None:
            return None
        if isinstance(d, str):
            d = date.fromisoformat(d)
        return (d - cycle_start_date).days + 1

    def _fmt_date(d: Any) -> str:
        cd = _cd(d)
        if cd is not None:
            return f"cycle day {cd}"
        if isinstance(d, (date, str)):
            return str(d)
        return "this cycle"

    parts: list[str] = []

    has_any_data = (
        coverline is not None
        or ovulation_date is not None
        or ovulation_confidence not in ("none", "missing", "")
        or fertile_start_date is not None
        or fertile_end_date is not None
        or luteal_length is not None
        or temp_count is not None
    )

    if not has_any_data:
        return (
            "No cycle analysis data is available yet. "
            "Begin tracking your basal body temperature daily to enable "
            "fertility analysis and ovulation detection."
        )

    if ovulation_confirmed and ovulation_date is not None:
        od_str = _fmt_date(ovulation_date)
        cl = f"{coverline}°{temp_unit}" if coverline is not None else "not determined"
        method = ovulation_method if ovulation_method and ovulation_method != "none" else "standard"
        parts.append(
            f"Ovulation was confirmed on {od_str} using the {method} method. "
            f"Your coverline is {cl} based on the 6 most recent pre-ovulatory temperatures."
        )
    elif ovulation_confidence == "possible":
        od_str = _fmt_date(ovulation_date) if ovulation_date else "this cycle"
        parts.append(
            f"Ovulation may have occurred around {od_str} but has not yet been confirmed. "
            "Continue tracking temperatures to establish a sustained shift."
        )
    elif coverline is not None:
        cl = f"{coverline}°{temp_unit}"
        parts.append(
            f"A coverline of {cl} has been computed, but a sustained temperature shift "
            "indicating ovulation has not yet been detected. Continue tracking daily temperatures."
        )
    elif temp_count is not None:
        parts.append(
            f"Insufficient temperature data to determine ovulation. "
            f"{temp_count} of the required 6 pre-ovulatory temperatures are available. "
            "Continue tracking daily."
        )
    else:
        parts.append(
            "Insufficient temperature data to determine ovulation. "
            "At least 6 pre-ovulatory temperatures are needed to compute a coverline. "
            "Continue tracking your basal body temperature daily."
        )

    if fertile_start_date is not None and fertile_end_date is not None:
        fsd_str = _fmt_date(fertile_start_date)
        fed_str = _fmt_date(fertile_end_date)
        parts.append(f"Your fertile window is from {fsd_str} to {fed_str}.")

    if luteal_length is not None:
        lp = f"Your luteal phase is {luteal_length} days."
        if luteal_phase_short:
            lp += " This is considered short (less than 10 days)."
        parts.append(lp)

    if phase:
        phase_display = phase.replace("_", " ")
        parts.append(f"You are currently in the {phase_display} phase.")
    elif cycle_day is not None:
        parts.append(f"You are on cycle day {cycle_day}.")

    return " ".join(parts)
