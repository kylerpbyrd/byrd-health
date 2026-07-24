from fertility_engine.coverline import compute_coverline, estimate_baseline


def test_coverline_empty_list_returns_none():
    assert compute_coverline([]) is None
    assert estimate_baseline([]) is None


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


def test_estimate_baseline_average_of_lowest_six():
    result = estimate_baseline([97.5, 97.0, 97.3, 97.2, 97.1, 97.4, 97.6, 97.8])
    assert result == 97.25


def test_estimate_baseline_fewer_than_six():
    result = estimate_baseline([97.5, 97.3, 97.1])
    assert result == round((97.1 + 97.3 + 97.5) / 3, 2)


def test_estimate_baseline_celsius():
    result = estimate_baseline([36.5, 36.3, 36.7], unit="C")
    assert result == round((36.3 + 36.5 + 36.7) / 3, 2)
