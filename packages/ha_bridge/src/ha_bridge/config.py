import os

from ha_bridge.bridge import HABridgeConfig


def read_ha_config() -> HABridgeConfig:
    return HABridgeConfig(
        temp_unit=os.environ.get("BBT_TEMP_UNIT", "F"),
        ha_sensor_entity=os.environ.get("BBT_HA_SENSOR_ENTITY", ""),
        poll_interval_seconds=int(os.environ.get("BBT_POLL_INTERVAL", "15")) * 60,
    )
