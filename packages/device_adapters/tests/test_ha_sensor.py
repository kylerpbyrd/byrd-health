import asyncio

import pytest

from device_adapters.adapters.ha_sensor import HASensorAdapter
from device_adapters.protocol import DeviceAdapter


def test_ha_sensor_implements_protocol():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=900)
    assert isinstance(adapter, DeviceAdapter)


def test_device_type_returns_ha_sensor():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=900)
    assert adapter.device_type == "ha_sensor"


def test_device_id_returns_entity_id():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = HASensorAdapter("sensor.bbt_bedroom", client, poll_interval_seconds=900)
    assert adapter.device_id == "sensor.bbt_bedroom"


@pytest.mark.asyncio
async def test_read_temperature_returns_none_before_connect():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=900)
    result = await adapter.read_temperature()
    assert result is None


@pytest.mark.asyncio
async def test_is_connected_false_before_connect():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=900)
    assert await adapter.is_connected() is False


@pytest.mark.asyncio
async def test_connect_disconnect_lifecycle():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "98.6"}

    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=900)

    await adapter.connect()
    assert await adapter.is_connected() is True

    await adapter.disconnect()
    assert await adapter.is_connected() is False


@pytest.mark.asyncio
async def test_read_temperature_returns_polled_value():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "97.83"}

    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=1)
    await adapter.connect()

    await asyncio.sleep(0.15)
    result = await adapter.read_temperature()
    assert result == 97.83

    await adapter.disconnect()


@pytest.mark.asyncio
async def test_read_temperature_stores_latest_value():
    from tests.conftest import MockHAClient

    client = MockHAClient()

    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=0.01)

    client._get_state_return = {"state": "97.5"}
    await adapter.connect()
    await asyncio.sleep(0.1)
    assert await adapter.read_temperature() == 97.5

    client._get_state_return = {"state": "98.2"}
    await asyncio.sleep(0.1)
    assert await adapter.read_temperature() == 98.2

    await adapter.disconnect()


@pytest.mark.asyncio
async def test_disconnect_stops_polling():
    from tests.conftest import MockHAClient

    client = MockHAClient()
    client._get_state_return = {"state": "97.5"}

    adapter = HASensorAdapter("sensor.temp", client, poll_interval_seconds=1)
    await adapter.connect()
    await asyncio.sleep(0.15)
    await adapter.disconnect()

    current = await adapter.read_temperature()

    client._get_state_return = {"state": "99.9"}
    await asyncio.sleep(0.15)

    assert await adapter.read_temperature() == current
