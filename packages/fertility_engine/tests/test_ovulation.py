from fertility_engine.ovulation import detect_ovulation


def _temperature(day, value, discarded=False):
    return {
        "date": f"2026-01-{day:02d}",
        "cycle_day": day,
        "temp_value": value,
        "is_discarded": discarded,
    }


def test_standard_three_day_shift_confirms_ovulation():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.5), _temperature(8, 97.6), _temperature(9, 97.7),
    ]

    result = detect_ovulation(temps)

    assert result.detected is True
    assert result.confidence == "confirmed"
    assert result.shift_start_date.isoformat() == "2026-01-07"
    assert result.ovulation_date.isoformat() == "2026-01-06"
    assert result.coverline == 97.4


def test_discarded_reading_does_not_prevent_a_confirmed_shift():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.8, discarded=True), _temperature(8, 97.5),
        _temperature(9, 97.6), _temperature(10, 97.7),
    ]

    result = detect_ovulation(temps)

    assert result.detected is True
    assert result.shift_start_date.isoformat() == "2026-01-08"


def test_conservative_method_extra_height_requirement():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.5), _temperature(8, 97.5), _temperature(9, 97.5),
    ]

    result = detect_ovulation(temps, method="conservative")

    assert result.detected is False


def test_conservative_method_passes_with_enough_height():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.5), _temperature(8, 97.5), _temperature(9, 97.8),
    ]

    result = detect_ovulation(temps, method="conservative")

    assert result.detected is True
    assert result.method == "conservative"


def test_witch_hat_exception():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.5), _temperature(8, 97.2),
        _temperature(9, 97.5), _temperature(10, 97.6),
    ]

    result = detect_ovulation(temps)

    assert result.detected is True
    assert result.confidence == "confirmed"
    assert "witchhat" in result.method


def test_insufficient_data_less_than_four_temps():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
    ]

    result = detect_ovulation(temps)

    assert result.detected is False
    assert result.confidence == "none"


def test_possible_detection_two_elevated():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.5), _temperature(8, 97.6),
    ]

    result = detect_ovulation(temps)

    assert result.detected is False
    assert result.confidence == "possible"
    assert result.consecutive_elevated == 2
    assert result.coverline is not None


def test_no_shift_detected():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1), _temperature(3, 97.2),
        _temperature(4, 97.1), _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(7, 97.1), _temperature(8, 97.3), _temperature(9, 97.2),
        _temperature(10, 97.4),
    ]

    result = detect_ovulation(temps)

    assert result.detected is False
    assert result.confidence == "none"


def test_gap_between_readings_prevents_detection():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1),
        _temperature(3, 97.2), _temperature(4, 97.1),
        _temperature(5, 97.3), _temperature(6, 97.2),
        _temperature(10, 97.7),
        _temperature(14, 97.8),
        _temperature(15, 97.9),
    ]

    result = detect_ovulation(temps)

    assert result.detected is False


def test_detection_not_before_min_cycle_day():
    temps = [
        _temperature(1, 97.0), _temperature(2, 97.1),
        _temperature(3, 97.5), _temperature(4, 97.6),
        _temperature(5, 97.7),
    ]

    result = detect_ovulation(temps)

    assert result.detected is False
