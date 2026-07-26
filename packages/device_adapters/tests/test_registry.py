import pytest
from device_adapters.registry import DeviceRegistry


class MockAdapter:
    def __init__(
        self,
        device_id: str,
        temperature: float | None = 98.6,
        connected: bool = True,
    ) -> None:
        self._device_id = device_id
        self._temperature = temperature
        self._connected = connected

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> str:
        return "mock"

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def read_temperature(self) -> float | None:
        return self._temperature

    async def is_connected(self) -> bool:
        return self._connected


def test_register_adds_adapter():
    registry = DeviceRegistry()
    adapter = MockAdapter("device-1")
    registry.register(adapter)
    assert True


def test_register_rejects_duplicate():
    registry = DeviceRegistry()
    adapter1 = MockAdapter("device-1")
    adapter2 = MockAdapter("device-1")
    registry.register(adapter1)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(adapter2)


@pytest.mark.asyncio
async def test_unregister_removes_adapter():
    registry = DeviceRegistry()
    adapter = MockAdapter("device-1")
    registry.register(adapter)
    registry.unregister("device-1")
    result = await registry.read_all()
    assert result == {}


def test_unregister_noop_unknown_id():
    registry = DeviceRegistry()
    registry.unregister("nonexistent")


@pytest.mark.asyncio
async def test_read_all_returns_connected_readings():
    registry = DeviceRegistry()
    registry.register(MockAdapter("a", temperature=97.5, connected=True))
    registry.register(MockAdapter("b", temperature=98.1, connected=True))
    registry.register(MockAdapter("c", temperature=99.0, connected=True))

    results = await registry.read_all()
    assert results == {"a": 97.5, "b": 98.1, "c": 99.0}


@pytest.mark.asyncio
async def test_read_all_skips_disconnected():
    registry = DeviceRegistry()
    registry.register(MockAdapter("connected", temperature=97.5, connected=True))
    registry.register(MockAdapter("disconnected", temperature=98.1, connected=False))

    results = await registry.read_all()
    assert "connected" in results
    assert "disconnected" not in results
    assert results == {"connected": 97.5}


@pytest.mark.asyncio
async def test_read_all_skips_none_reading():
    registry = DeviceRegistry()
    registry.register(MockAdapter("a", temperature=97.5, connected=True))
    registry.register(MockAdapter("b", temperature=None, connected=True))

    results = await registry.read_all()
    assert results == {"a": 97.5}


@pytest.mark.asyncio
async def test_read_all_empty_registry():
    registry = DeviceRegistry()
    results = await registry.read_all()
    assert results == {}
