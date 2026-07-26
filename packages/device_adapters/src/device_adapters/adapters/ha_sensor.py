from ha_bridge.client import HAClient
from ha_bridge.poller import SensorPoller


class HASensorAdapter:
    def __init__(
        self,
        entity_id: str,
        client: HAClient,
        poll_interval_seconds: int,
    ) -> None:
        self._entity_id = entity_id
        self._poller = SensorPoller(client, poll_interval_seconds)
        self._latest_reading: float | None = None
        self._connected = False

    @property
    def device_id(self) -> str:
        return self._entity_id

    @property
    def device_type(self) -> str:
        return "ha_sensor"

    async def connect(self) -> None:
        await self._poller.add_sensor(self._entity_id)
        await self._poller.start(self._on_reading)
        self._connected = True

    async def disconnect(self) -> None:
        await self._poller.stop()
        self._connected = False

    async def read_temperature(self) -> float | None:
        return self._latest_reading

    async def is_connected(self) -> bool:
        return self._connected

    async def _on_reading(self, entity_id: str, value: float) -> None:
        if entity_id == self._entity_id:
            self._latest_reading = value
