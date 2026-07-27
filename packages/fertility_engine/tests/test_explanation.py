from datetime import date

from fertility_engine.explanation import generate_explanation
from fertility_engine.models import CycleInsights


class TestGenerateExplanation:
    def test_confirmed_ovulation_full_insights(self):
        insights = CycleInsights(
            coverline=97.4,
            ovulation_date=date(2026, 1, 15),
            ovulation_confirmed=True,
            ovulation_confidence="confirmed",
            ovulation_method="standard",
            fertile_start_date=date(2026, 1, 11),
            fertile_end_date=date(2026, 1, 16),
            luteal_length=14,
            luteal_phase_short=False,
            consecutive_elevated_temps=3,
            engine_version="1.0.0",
        )
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 1, 1),
        )

        assert "Ovulation was confirmed on cycle day 15" in result
        assert "standard method" in result
        assert "coverline is 97.4°F" in result
        assert "fertile window is from cycle day 11 to cycle day 16" in result
        assert "luteal phase is 14 days" in result
        assert "{" not in result
        assert "}" not in result

    def test_possible_ovulation_not_confirmed(self):
        insights = {
            "coverline": 97.4,
            "ovulation_date": date(2026, 1, 20),
            "ovulation_confirmed": False,
            "ovulation_confidence": "possible",
            "ovulation_method": "standard",
            "fertile_start_date": None,
            "fertile_end_date": None,
            "luteal_length": None,
        }
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 1, 1),
        )

        assert "may have occurred around cycle day 20" in result
        assert "not yet been confirmed" in result
        assert "Continue tracking temperatures" in result
        assert "fertile window" not in result
        assert "luteal phase" not in result
        assert "{" not in result
        assert "}" not in result

    def test_insufficient_data_with_temp_count(self):
        insights = {}
        result = generate_explanation(
            insights,
            temp_unit="F",
            temp_count=2,
        )

        assert "Insufficient temperature data" in result
        assert "2 of the required 6" in result
        assert "{" not in result
        assert "}" not in result

    def test_no_data_at_all(self):
        insights = {}
        result = generate_explanation(insights, temp_unit="F")

        assert "No cycle analysis data is available yet" in result
        assert "{" not in result
        assert "}" not in result

    def test_coverline_computed_no_ovulation(self):
        insights = {
            "coverline": 97.4,
            "ovulation_date": None,
            "ovulation_confirmed": False,
            "ovulation_confidence": "none",
            "ovulation_method": "none",
            "fertile_start_date": None,
            "fertile_end_date": None,
            "luteal_length": None,
            "phase": "pre_ovulatory",
        }
        result = generate_explanation(
            insights,
            temp_unit="C",
            cycle_start_date=date(2026, 1, 1),
        )

        assert "coverline of 97.4°C has been computed" in result
        assert "sustained temperature shift" in result
        assert "not yet been detected" in result
        assert "pre ovulatory phase" in result
        assert "{" not in result
        assert "}" not in result

    def test_with_phase_and_cycle_day(self):
        insights = {
            "coverline": 97.4,
            "ovulation_date": date(2026, 1, 15),
            "ovulation_confirmed": True,
            "ovulation_confidence": "confirmed",
            "ovulation_method": "conservative",
            "fertile_start_date": date(2026, 1, 11),
            "fertile_end_date": date(2026, 1, 16),
            "luteal_length": 14,
            "luteal_phase_short": False,
            "phase": "luteal",
            "cycle_day": 22,
        }
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 1, 1),
        )

        assert "conservative method" in result
        assert "luteal phase" in result
        assert "{" not in result
        assert "}" not in result

    def test_short_luteal_phase(self):
        insights = {
            "coverline": 97.4,
            "ovulation_date": date(2026, 1, 22),
            "ovulation_confirmed": True,
            "ovulation_confidence": "confirmed",
            "ovulation_method": "standard",
            "luteal_length": 8,
            "luteal_phase_short": True,
            "phase": "luteal",
        }
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 1, 1),
        )

        assert "luteal phase is 8 days" in result
        assert "short (less than 10 days)" in result
        assert "{" not in result
        assert "}" not in result

    def test_dict_with_string_date(self):
        insights = {
            "coverline": 97.6,
            "ovulation_date": "2026-02-14",
            "ovulation_confirmed": True,
            "ovulation_confidence": "confirmed",
            "ovulation_method": "standard",
            "fertile_start_date": date(2026, 2, 10),
            "fertile_end_date": date(2026, 2, 15),
            "luteal_length": 13,
            "phase": "luteal",
        }
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 2, 1),
        )

        assert "Ovulation was confirmed on cycle day 14" in result
        assert "{" not in result
        assert "}" not in result

    def test_possible_without_ovulation_date(self):
        insights = {
            "ovulation_confidence": "possible",
        }
        result = generate_explanation(
            insights,
            temp_unit="F",
        )

        assert "may have occurred around this cycle" in result
        assert "not yet been confirmed" in result
        assert "{" not in result
        assert "}" not in result

    def test_cycleinsights_object_input(self):
        insights = CycleInsights(
            coverline=97.5,
            ovulation_date=date(2026, 3, 10),
            ovulation_confirmed=True,
            ovulation_confidence="confirmed",
            ovulation_method="standard",
            fertile_start_date=date(2026, 3, 6),
            fertile_end_date=date(2026, 3, 11),
            luteal_length=12,
            luteal_phase_short=False,
            consecutive_elevated_temps=3,
            engine_version="1.0.0",
        )
        result = generate_explanation(
            insights,
            temp_unit="F",
            cycle_start_date=date(2026, 3, 1),
        )

        assert "Ovulation was confirmed on cycle day 10" in result
        assert "97.5°F" in result
        assert "{" not in result
        assert "}" not in result
