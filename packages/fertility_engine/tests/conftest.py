from datetime import date

import pytest

from fertility_engine.models import FertilitySignsRecord, ProfileSettings, TemperatureRecord


@pytest.fixture
def sample_temps() -> list[TemperatureRecord]:
    return [
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


@pytest.fixture
def sample_signs() -> list[FertilitySignsRecord]:
    return [
        FertilitySignsRecord(date=date(2026, 1, d), cervical_mucus=m)
        for d, m in [
            (1, "dry"), (2, "dry"), (3, "dry"), (4, "dry"), (5, "dry"),
            (6, "dry"), (7, "dry"), (8, "dry"), (9, "dry"), (10, "sticky"),
            (11, "sticky"), (12, "creamy"), (13, "watery"), (14, "egg_white"),
            (15, "egg_white"), (16, "watery"), (17, "creamy"), (18, "sticky"),
            (19, "dry"), (20, "dry"), (21, "dry"), (22, "dry"), (23, "dry"),
            (24, "dry"), (25, "dry"), (26, "dry"), (27, "dry"), (28, "dry"),
            (29, "dry"), (30, "dry"),
        ]
    ]


@pytest.fixture
def sample_profile() -> ProfileSettings:
    return ProfileSettings(temp_unit="F", interpretation_method="standard")
