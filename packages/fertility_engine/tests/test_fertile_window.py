from datetime import date

from fertility_engine.fertile_window import compute_fertile_window, get_cycle_phase
from fertility_engine.models import FertileWindowResult, OvulationResult


def _no_ovulation():
    return OvulationResult(detected=False)


def _confirmed_ovulation():
    return OvulationResult(
        detected=True,
        ovulation_date=date(2026, 1, 14),
        shift_start_date=date(2026, 1, 15),
        coverline=97.4,
        method="standard",
        confidence="confirmed",
        consecutive_elevated=3,
    )


def test_fertile_mucus_moves_window_earlier_than_calendar_rule():
    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=_no_ovulation(),
        fertility_signs=[{"date": "2026-01-04", "cervical_mucus": "egg_white"}],
        past_cycle_lengths=[30],
    )

    assert window.fertile_start == date(2026, 1, 4)
    assert window.calendar_rule_day == 12
    assert window.mucus_triggered is True


def test_calendar_rule_no_cycle_history_defaults_to_day_8():
    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=_no_ovulation(),
        fertility_signs=[],
        past_cycle_lengths=[],
    )

    assert window.fertile_start == date(2026, 1, 8)
    assert window.calendar_rule_day == 8
    assert window.mucus_triggered is False


def test_calendar_rule_shortest_cycle_minimum_21():
    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=_no_ovulation(),
        fertility_signs=[],
        past_cycle_lengths=[18, 25, 30],
    )

    assert window.fertile_start == date(2026, 1, 3)
    assert window.calendar_rule_day == 3


def test_confirmed_ovulation_sets_post_ovulatory_infertile():
    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=_confirmed_ovulation(),
        fertility_signs=[],
        past_cycle_lengths=[],
    )

    assert window.post_ovulatory_infertile == date(2026, 1, 18)
    assert window.fertile_end == date(2026, 1, 17)


def test_possible_ovulation_uses_conservative_estimate():
    ov = OvulationResult(
        detected=False,
        ovulation_date=date(2026, 1, 14),
        shift_start_date=date(2026, 1, 15),
        confidence="possible",
    )

    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=ov,
        fertility_signs=[],
        past_cycle_lengths=[],
    )

    assert window.fertile_end == date(2026, 1, 16)
    assert window.post_ovulatory_infertile == date(2026, 1, 17)


def test_mucus_case_insensitive():
    window = compute_fertile_window(
        cycle_start_date=date(2026, 1, 1),
        ovulation_result=_no_ovulation(),
        fertility_signs=[{"date": "2026-01-05", "cervical_mucus": "EGG_WHITE"}],
        past_cycle_lengths=[],
    )

    assert window.fertile_start == date(2026, 1, 5)
    assert window.mucus_triggered is True


def test_get_cycle_phase_menstruation():
    phase = get_cycle_phase(
        current_date=date(2026, 1, 3),
        cycle_start=date(2026, 1, 1),
        flow_days=["2026-01-01", "2026-01-02", "2026-01-03"],
        fertile_window=FertileWindowResult(
            fertile_start=date(2026, 1, 8),
            fertile_end=date(2026, 1, 17),
            calendar_rule_day=8,
        ),
        ovulation_date=None,
        ovulation_confirmed=False,
        post_ov_infertile=None,
    )

    assert phase == "menstruation"


def test_get_cycle_phase_luteal():
    phase = get_cycle_phase(
        current_date=date(2026, 1, 20),
        cycle_start=date(2026, 1, 1),
        flow_days=["2026-01-01", "2026-01-02", "2026-01-03"],
        fertile_window=FertileWindowResult(
            fertile_start=date(2026, 1, 8),
            fertile_end=date(2026, 1, 17),
            post_ovulatory_infertile=date(2026, 1, 18),
            calendar_rule_day=8,
        ),
        ovulation_date=date(2026, 1, 14),
        ovulation_confirmed=True,
        post_ov_infertile=date(2026, 1, 18),
    )

    assert phase == "luteal"


def test_get_cycle_phase_ovulation():
    phase = get_cycle_phase(
        current_date=date(2026, 1, 14),
        cycle_start=date(2026, 1, 1),
        flow_days=[],
        fertile_window=FertileWindowResult(
            fertile_start=date(2026, 1, 8),
            fertile_end=date(2026, 1, 17),
            calendar_rule_day=8,
        ),
        ovulation_date=date(2026, 1, 14),
        ovulation_confirmed=True,
        post_ov_infertile=date(2026, 1, 18),
    )

    assert phase == "ovulation"


def test_get_cycle_phase_fertile():
    phase = get_cycle_phase(
        current_date=date(2026, 1, 10),
        cycle_start=date(2026, 1, 1),
        flow_days=[],
        fertile_window=FertileWindowResult(
            fertile_start=date(2026, 1, 8),
            fertile_end=date(2026, 1, 17),
            calendar_rule_day=8,
        ),
        ovulation_date=None,
        ovulation_confirmed=False,
        post_ov_infertile=None,
    )

    assert phase == "fertile"


def test_get_cycle_phase_pre_ovulatory():
    phase = get_cycle_phase(
        current_date=date(2026, 1, 5),
        cycle_start=date(2026, 1, 1),
        flow_days=[],
        fertile_window=FertileWindowResult(
            fertile_start=date(2026, 1, 8),
            fertile_end=date(2026, 1, 17),
            calendar_rule_day=8,
        ),
        ovulation_date=None,
        ovulation_confirmed=False,
        post_ov_infertile=None,
    )

    assert phase == "pre_ovulatory"
