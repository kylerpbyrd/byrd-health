
THRESHOLD_F: float = 0.1
THRESHOLD_C: float = 0.05


def compute_coverline(pre_shift_temps: list[float], unit: str = "F") -> float | None:
    if not pre_shift_temps:
        return None
    sample = pre_shift_temps[-6:]
    threshold = THRESHOLD_F if unit == "F" else THRESHOLD_C
    return round(max(sample) + threshold, 2)
