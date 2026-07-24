import asyncio


async def test_poller_reads_sensor_calls_callback(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = {"state": "98.6"}
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.temp")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) > 0
    assert results[0] == ("sensor.temp", 98.6)


async def test_poller_skips_unknown_state(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = {"state": "unknown"}
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.temp")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) == 0


async def test_poller_skips_unavailable_state(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = {"state": "unavailable"}
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.temp")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) == 0


async def test_poller_skips_none_response(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = None
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.temp")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) == 0


async def test_poller_skips_empty_entity_id(mock_client):
    from ha_bridge.poller import SensorPoller

    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) == 0


async def test_poller_callback_exception_handled(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = {"state": "42"}
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.temp")

    async def cb(entity_id: str, value: float) -> None:
        raise RuntimeError("boom")

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()


async def test_multiple_sensors(mock_client):
    from ha_bridge.poller import SensorPoller

    mock_client._get_state_return = {"state": "36.6"}
    poller = SensorPoller(mock_client, interval_seconds=0.01)
    await poller.add_sensor("sensor.a")
    await poller.add_sensor("sensor.b")

    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await poller.start(cb)
    await asyncio.sleep(0.05)
    await poller.stop()

    assert len(results) >= 2
    entities = {r[0] for r in results}
    assert entities == {"sensor.a", "sensor.b"}
