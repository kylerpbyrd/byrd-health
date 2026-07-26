import pytest

from device_adapters.adapters.esphome import ESPHomeAdapter, ESPHomeConfig
from device_adapters.protocol import DeviceAdapter


def test_esphome_adapter_implements_protocol():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    assert isinstance(adapter, DeviceAdapter)


def test_device_type_returns_esphome():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    assert adapter.device_type == "esphome"


def test_device_id_matches_entity():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    assert adapter.device_id == "esphome_sensor_esp32_bbt_temperature"


def test_device_id_uses_custom_when_provided():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client, device_id="custom-esphome-1")
    assert adapter.device_id == "custom-esphome-1"


@pytest.mark.asyncio
async def test_connect_sets_connected():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "98.6", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    await adapter.connect()
    assert await adapter.is_connected() is True


@pytest.mark.asyncio
async def test_connect_fails_on_unavailable():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = None

    adapter = ESPHomeAdapter("sensor.nonexistent", client)
    await adapter.connect()
    assert await adapter.is_connected() is False


@pytest.mark.asyncio
async def test_read_temperature_returns_float():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "98.6", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    result = await adapter.read_temperature()
    assert result == 98.6


@pytest.mark.asyncio
async def test_read_temperature_returns_none_for_unknown():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "unknown", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    result = await adapter.read_temperature()
    assert result is None


@pytest.mark.asyncio
async def test_read_temperature_returns_none_for_unavailable():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "unavailable", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    result = await adapter.read_temperature()
    assert result is None


@pytest.mark.asyncio
async def test_read_temperature_returns_none_for_empty_state():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    result = await adapter.read_temperature()
    assert result is None


@pytest.mark.asyncio
async def test_disconnect_sets_not_connected():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "98.6", "entity_id": "sensor.esp32_bbt_temperature"}

    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    await adapter.connect()
    assert await adapter.is_connected() is True

    await adapter.disconnect()
    assert await adapter.is_connected() is False


@pytest.mark.asyncio
async def test_is_connected_reflects_state():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = ESPHomeAdapter("sensor.esp32_bbt_temperature", client)
    assert await adapter.is_connected() is False

    client._get_state_return = {"state": "98.6"}
    await adapter.connect()
    assert await adapter.is_connected() is True


def test_esphome_config_defaults():
    config = ESPHomeConfig("sensor.test")
    assert config.entity_id == "sensor.test"
    assert config.name == "ESPHome Sensor"


def test_esphome_config_custom_name():
    config = ESPHomeConfig("sensor.temp_bedroom", name="Bedroom Sensor")
    assert config.entity_id == "sensor.temp_bedroom"
    assert config.name == "Bedroom Sensor"
