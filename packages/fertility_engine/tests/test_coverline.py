from fertility_engine.coverline import compute_coverline


def test_coverline_empty_list_returns_none():
    assert compute_coverline([]) is None


def test_coverline_single_value():
    result = compute_coverline([97.5])
    assert result == 97.6


def test_coverline_uses_last_six_and_fahrenheit_threshold():
    result = compute_coverline([97.0, 97.1, 97.2, 97.3, 97.4, 97.5, 98.0])
    assert result == 98.1


def test_coverline_celsius_threshold():
    result = compute_coverline([36.4, 36.5], unit="C")
    assert result == 36.55


def test_coverline_fewer_than_six_readings():
    result = compute_coverline([97.0, 97.1, 97.2])
    assert result == 97.3

