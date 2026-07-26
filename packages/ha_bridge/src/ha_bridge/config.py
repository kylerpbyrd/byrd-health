from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ha_bridge.bridge import HABridgeConfig


def _bool_env(key: str, default: bool = True) -> bool:
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default


def read_ha_config() -> HABridgeConfig:
    from ha_bridge.bridge import HABridgeConfig

    return HABridgeConfig(
        temp_unit=os.environ.get("BBT_TEMP_UNIT", "F"),
        ha_sensor_entity=os.environ.get("BBT_HA_SENSOR_ENTITY", ""),
        poll_interval_seconds=int(os.environ.get("BBT_POLL_INTERVAL", "15")) * 60,
        notify_temp_reminder=_bool_env("BBT_NOTIFY_TEMP", True),
        notify_temp_reminder_time=os.environ.get("BBT_NOTIFY_TEMP_TIME", "07:00"),
        notify_fertile_window=_bool_env("BBT_NOTIFY_FERTILE", True),
        notify_period_prediction=_bool_env("BBT_NOTIFY_PERIOD", True),
        notify_ovulation_detected=_bool_env("BBT_NOTIFY_OVULATION", True),
    )
