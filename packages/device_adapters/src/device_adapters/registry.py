from device_adapters.protocol import DeviceAdapter


class DeviceRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, DeviceAdapter] = {}

    def register(self, adapter: DeviceAdapter) -> None:
        if adapter.device_id in self._adapters:
            raise ValueError(f"Device '{adapter.device_id}' already registered")
        self._adapters[adapter.device_id] = adapter

    def unregister(self, device_id: str) -> None:
        self._adapters.pop(device_id, None)

    def list_adapters(self) -> list[dict]:
        return [
            {"device_id": device_id, "device_type": adapter.device_type}
            for device_id, adapter in self._adapters.items()
        ]

    def get_adapter(self, device_id: str) -> DeviceAdapter | None:
        return self._adapters.get(device_id)

    async def read_all(self) -> dict[str, float]:
        results: dict[str, float] = {}
        for device_id, adapter in self._adapters.items():
            if await adapter.is_connected():
                temp = await adapter.read_temperature()
                if temp is not None:
                    results[device_id] = temp
        return results
