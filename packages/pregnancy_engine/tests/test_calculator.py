from datetime import date

from pregnancy_engine.calculator import (
    calculate_current_week,
    calculate_days_remaining,
    calculate_due_date,
    calculate_trimester,
)


def test_due_date_from_ovulation():
    assert calculate_due_date(ovulation_date=date(2026, 1, 15)) == date(2026, 10, 8)


def test_due_date_from_lmp():
    assert calculate_due_date(lmp_date=date(2026, 1, 1)) == date(2026, 10, 8)


def test_due_date_prefers_ovulation():
    result = calculate_due_date(ovulation_date=date(2026, 1, 15), lmp_date=date(2026, 1, 1))
    assert result == date(2026, 10, 8)


def test_due_date_none_when_no_input():
    assert calculate_due_date() is None


def test_current_week():
    lmp = date(2026, 1, 1)
    ref = date(2026, 1, 15)
    assert calculate_current_week(lmp, ref) == 3


def test_trimester():
    assert calculate_trimester(5) == 1
    assert calculate_trimester(13) == 1
    assert calculate_trimester(14) == 2
    assert calculate_trimester(26) == 2
    assert calculate_trimester(27) == 3


def test_days_remaining():
    due = date(2026, 10, 8)
    ref = date(2026, 10, 1)
    assert calculate_days_remaining(due, ref) == 7
