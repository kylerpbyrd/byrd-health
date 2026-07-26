from datetime import date, timedelta


def predict_next_period(
    cycle_start_date: date,
    ovulation_date: date | None,
    ovulation_confirmed: bool,
    average_luteal_length: int,
    average_cycle_length: int,
) -> date | None:
    if ovulation_confirmed and ovulation_date:
        return ovulation_date + timedelta(days=average_luteal_length + 1)

    return cycle_start_date + timedelta(days=average_cycle_length)


def get_current_cycle_day(cycle_start_date: date) -> int:
    return max(1, (date.today() - cycle_start_date).days + 1)
