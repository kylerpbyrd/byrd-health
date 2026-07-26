from datetime import date, timedelta

from fertility_engine.models import FertileWindowResult, OvulationResult

_FERTILE_MUCUS: frozenset[str] = frozenset({"watery", "egg_white"})

_MIN_CYCLE: int = 21
_DEFAULT_FERTILE_START_DAY: int = 8


def _to_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def compute_fertile_window(
    cycle_start_date: date,
    ovulation_result: OvulationResult,
    fertility_signs: list[dict],
    past_cycle_lengths: list[int],
    unit: str = "F",
) -> FertileWindowResult:
    if past_cycle_lengths:
        shortest = max(min(past_cycle_lengths), _MIN_CYCLE)
        calendar_day = max(1, shortest - 18)
    else:
        calendar_day = _DEFAULT_FERTILE_START_DAY

    calendar_date = cycle_start_date + timedelta(days=calendar_day - 1)

    mucus_date: date | None = None
    for sign in sorted(fertility_signs, key=lambda s: s["date"]):
        if sign.get("cervical_mucus", "").lower() in _FERTILE_MUCUS:
            mucus_date = _to_date(sign["date"])
            break

    if mucus_date is not None:
        fertile_start = min(calendar_date, mucus_date)
        mucus_triggered = mucus_date < calendar_date
    else:
        fertile_start = calendar_date
        mucus_triggered = False

    fertile_end: date | None = None
    post_ov_infertile: date | None = None

    if ovulation_result.detected and ovulation_result.shift_start_date:
        shift_start = ovulation_result.shift_start_date
        post_ov_infertile = shift_start + timedelta(days=3)
        fertile_end = post_ov_infertile - timedelta(days=1)
    elif ovulation_result.ovulation_date:
        ov_date = ovulation_result.ovulation_date
        fertile_end = ov_date + timedelta(days=2)
        post_ov_infertile = fertile_end + timedelta(days=1)

    return FertileWindowResult(
        fertile_start=fertile_start,
        fertile_end=fertile_end,
        post_ovulatory_infertile=post_ov_infertile,
        calendar_rule_day=calendar_day,
        mucus_triggered=mucus_triggered,
    )


def get_cycle_phase(
    current_date: date,
    cycle_start: date,
    flow_days: list[str],
    fertile_window: FertileWindowResult,
    ovulation_date: date | None,
    ovulation_confirmed: bool,
    post_ov_infertile: date | None,
) -> str:
    today_str = current_date.isoformat()

    if today_str in flow_days:
        return "menstruation"

    if post_ov_infertile:
        if current_date >= post_ov_infertile:
            return "luteal"

    if ovulation_confirmed and ovulation_date and current_date == ovulation_date:
        return "ovulation"

    fs = fertile_window.fertile_start
    fe = fertile_window.fertile_end
    if fs and fe:
        if fs <= current_date <= fe:
            if ovulation_confirmed and ovulation_date:
                if current_date > ovulation_date:
                    return "luteal"
            return "fertile"

    return "pre_ovulatory"
