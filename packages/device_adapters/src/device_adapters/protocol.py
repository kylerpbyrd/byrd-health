from typing import Protocol, runtime_checkable


@runtime_checkable
class DeviceAdapter(Protocol):
    """Protocol that all device adapters must implement."""

    @property
    def device_id(self) -> str: ...

    @property
    def device_type(self) -> str: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    async def read_temperature(self) -> float | None: ...

    async def is_connected(self) -> bool: ...
