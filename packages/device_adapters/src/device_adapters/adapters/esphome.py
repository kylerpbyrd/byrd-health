from __future__ import annotations

from dataclasses import dataclass

from ha_bridge.client import HAClient


@dataclass
class ESPHomeConfig:
    entity_id: str
    name: str = "ESPHome Sensor"


class ESPHomeAdapter:
    """Connects to an ESPHome device via HA API and reads sensor values."""

    def __init__(
        self,
        entity_id: str,
        client: HAClient,
        device_id: str | None = None,
    ) -> None:
        self._entity_id = entity_id
        self._client = client
        self._device_id = device_id or f"esphome_{entity_id.replace('.', '_')}"
        self._connected = False

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> str:
        return "esphome"

    async def connect(self) -> None:
        state = await self._client.get_state(self._entity_id)
        self._connected = state is not None

    async def disconnect(self) -> None:
        self._connected = False

    async def read_temperature(self) -> float | None:
        data = await self._client.get_state(self._entity_id)
        if data and data.get("state") not in ("unknown", "unavailable", ""):
            try:
                return float(data["state"])
            except (ValueError, TypeError):
                pass
        return None

    async def is_connected(self) -> bool:
        return self._connected
