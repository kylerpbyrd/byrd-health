from datetime import date


def calculate_due_date(ovulation_date: date | None = None, lmp_date: date | None = None) -> date | None:
    if ovulation_date is not None:
        return ovulation_date + _days(266)
    if lmp_date is not None:
        return lmp_date + _days(280)
    return None


def calculate_current_week(lmp_date: date, reference_date: date | None = None) -> int:
    if reference_date is None:
        reference_date = date.today()
    delta = (reference_date - lmp_date).days
    week = (delta // 7) + 1
    return max(week, 1)


def calculate_trimester(current_week: int) -> int:
    if current_week <= 13:
        return 1
    if current_week <= 26:
        return 2
    return 3


def calculate_days_remaining(due_date: date, reference_date: date | None = None) -> int:
    if reference_date is None:
        reference_date = date.today()
    return (due_date - reference_date).days


def _days(n: int) -> "timedelta":
    from datetime import timedelta

    return timedelta(days=n)
