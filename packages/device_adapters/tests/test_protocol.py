from device_adapters.protocol import DeviceAdapter


class FullAdapter:
    @property
    def device_id(self) -> str:
        return "test-001"

    @property
    def device_type(self) -> str:
        return "mock"

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def read_temperature(self) -> float | None:
        return 98.6

    async def is_connected(self) -> bool:
        return True


class MissingMethods:
    @property
    def device_id(self) -> str:
        return "incomplete"


class MissingProperty:
    @property
    def device_id(self) -> str:
        return "noprop"

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def read_temperature(self) -> float | None:
        return None

    async def is_connected(self) -> bool:
        return False


def test_full_adapter_isinstance_passes():
    adapter = FullAdapter()
    assert isinstance(adapter, DeviceAdapter)


def test_missing_methods_isinstance_fails():
    adapter = MissingMethods()
    assert not isinstance(adapter, DeviceAdapter)


def test_missing_property_isinstance_fails():
    adapter = MissingProperty()
    assert not isinstance(adapter, DeviceAdapter)
