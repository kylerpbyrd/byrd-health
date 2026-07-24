from datetime import date, timedelta
from typing import Optional, Union

from fertility_engine.coverline import compute_coverline
from fertility_engine.models import OvulationResult

MIN_CYCLE_DAY: int = 6

_EXTRA_F: float = 0.2
_EXTRA_C: float = 0.1

_MAX_GAP: int = 2


def _to_date(value: Union[str, date]) -> date:
    """Coerce a string or date object to a date."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def detect_ovulation(
    temps: list[dict],
    unit: str = "F",
    method: str = "standard",
) -> OvulationResult:
    active = sorted(
        [t for t in temps if not t.get("is_discarded", False)],
        key=lambda t: t["cycle_day"],
    )
    n = len(active)
    if n < 4:
        return OvulationResult(detected=False)

    extra = _EXTRA_F if unit == "F" else _EXTRA_C

    for i in range(n):
        if active[i]["cycle_day"] < MIN_CYCLE_DAY:
            continue

        pre_values = [active[j]["temp_value"] for j in range(i)]
        if len(pre_values) < 3:
            continue

        coverline = compute_coverline(pre_values, unit)
        if coverline is None:
            continue

        if i + 2 >= n:
            break

        t0, t1, t2 = active[i], active[i + 1], active[i + 2]

        if (t1["cycle_day"] - t0["cycle_day"] > _MAX_GAP
                or t2["cycle_day"] - t1["cycle_day"] > _MAX_GAP):
            continue

        all_above = (
            t0["temp_value"] > coverline
            and t1["temp_value"] > coverline
            and t2["temp_value"] > coverline
        )

        if all_above:
            if method == "conservative" and t2["temp_value"] < coverline + extra:
                continue

            ov_date = _to_date(t0["date"]) - timedelta(days=1)
            return OvulationResult(
                detected=True,
                ovulation_date=ov_date,
                shift_start_date=_to_date(t0["date"]),
                coverline=coverline,
                method=method,
                confidence="confirmed",
                consecutive_elevated=3,
            )

        if (i + 3 < n
                and t0["temp_value"] > coverline
                and t2["temp_value"] > coverline):
            t3 = active[i + 3]
            if (t3["cycle_day"] - t2["cycle_day"] <= _MAX_GAP
                    and t3["temp_value"] > coverline):
                ov_date = _to_date(t0["date"]) - timedelta(days=1)
                return OvulationResult(
                    detected=True,
                    ovulation_date=ov_date,
                    shift_start_date=_to_date(t0["date"]),
                    coverline=coverline,
                    method=f"{method}_witchhat",
                    confidence="confirmed",
                    consecutive_elevated=3,
                )

    for i in range(n):
        if active[i]["cycle_day"] < MIN_CYCLE_DAY:
            continue

        pre_values = [active[j]["temp_value"] for j in range(i)]
        if len(pre_values) < 3:
            continue

        coverline = compute_coverline(pre_values, unit)
        if coverline is None:
            continue

        if i + 1 >= n:
            break

        t0, t1 = active[i], active[i + 1]
        if t1["cycle_day"] - t0["cycle_day"] > _MAX_GAP:
            continue
        if t0["temp_value"] > coverline and t1["temp_value"] > coverline:
            ov_date = _to_date(t0["date"]) - timedelta(days=1)
            return OvulationResult(
                detected=False,
                ovulation_date=ov_date,
                shift_start_date=_to_date(t0["date"]),
                coverline=coverline,
                method=method,
                confidence="possible",
                consecutive_elevated=2,
            )

    all_values = [t["temp_value"] for t in active]
    est = compute_coverline(all_values, unit) if all_values else None
    return OvulationResult(detected=False, coverline=est)
