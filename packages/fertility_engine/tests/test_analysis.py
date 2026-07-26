
from datetime import date

from fertility_engine.analysis import analyze_cycle
from fertility_engine.models import ProfileSettings


def test_full_pipeline_with_synthetic_cycle(sample_temps, sample_signs, sample_profile):
    insights = analyze_cycle(
        temps=sample_temps,
        signs=sample_signs,
        profile_settings=sample_profile,
        past_cycle_lengths=[28, 29, 30],
        cycle_start_date=date(2026, 1, 1),
        cycle_end_date=date(2026, 1, 30),
    )

    assert insights.engine_version == "1.0.0"
    assert insights.ovulation_confirmed is True
    assert insights.ovulation_confidence == "confirmed"
    assert insights.ovulation_method == "standard"
    assert insights.ovulation_date is not None
    assert insights.coverline is not None
    assert insights.fertile_start_date is not None
    assert insights.fertile_end_date is not None
    assert insights.post_ovulatory_infertile_date is not None
    assert insights.luteal_length is not None
    assert isinstance(insights.luteal_length, int)
    assert isinstance(insights.consecutive_elevated_temps, int)
    assert isinstance(insights.pregnancy_indicator, bool)
    assert isinstance(insights.luteal_phase_short, bool)


def test_full_pipeline_without_cycle_end_date(sample_temps, sample_signs, sample_profile):
    insights = analyze_cycle(
        temps=sample_temps,
        signs=sample_signs,
        profile_settings=sample_profile,
        past_cycle_lengths=[28, 29, 30],
        cycle_start_date=date(2026, 1, 1),
    )

    assert insights.luteal_length is None
    assert insights.luteal_phase_short is False


def test_full_pipeline_conservative_method(sample_temps, sample_signs):
    profile = ProfileSettings(temp_unit="F", interpretation_method="conservative")

    insights = analyze_cycle(
        temps=sample_temps,
        signs=sample_signs,
        profile_settings=profile,
        past_cycle_lengths=[28, 29, 30],
        cycle_start_date=date(2026, 1, 1),
    )

    assert insights.engine_version == "1.0.0"


def test_full_pipeline_all_fields_populated():
    from datetime import date

    from fertility_engine.models import FertilitySignsRecord, TemperatureRecord

    temps = [
        TemperatureRecord(date=date(2026, 1, d), temp_value=v, cycle_day=d)
        for d, v in [
            (1, 97.2), (2, 97.0), (3, 97.1), (4, 97.3), (5, 97.2), (6, 97.0),
            (7, 97.1), (8, 97.4), (9, 97.3), (10, 97.0), (11, 97.2), (12, 97.1),
            (13, 97.4), (14, 97.2),
            (15, 97.7), (16, 97.8), (17, 97.7),
            (18, 97.8), (19, 97.7), (20, 97.9), (21, 98.0), (22, 97.9),
            (23, 98.1), (24, 98.0), (25, 98.2), (26, 98.0), (27, 98.1),
            (28, 98.3), (29, 98.2), (30, 98.1),
        ]
    ]

    signs = [
        FertilitySignsRecord(date=date(2026, 1, 13), cervical_mucus="watery"),
        FertilitySignsRecord(date=date(2026, 1, 14), cervical_mucus="egg_white"),
    ]

    profile = ProfileSettings(temp_unit="F", interpretation_method="standard")

    insights = analyze_cycle(
        temps=temps,
        signs=signs,
        profile_settings=profile,
        past_cycle_lengths=[28, 29, 30],
        cycle_start_date=date(2026, 1, 1),
        cycle_end_date=date(2026, 1, 30),
    )

    assert insights.ovulation_confirmed is True
    assert insights.ovulation_date is not None
    assert insights.coverline is not None
    assert insights.fertile_start_date is not None
    assert insights.fertile_end_date is not None
    assert insights.post_ovulatory_infertile_date is not None
    assert insights.luteal_length is not None
    assert insights.consecutive_elevated_temps > 0
    assert insights.engine_version == "1.0.0"
