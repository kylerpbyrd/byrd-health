import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable

from ha_bridge.client import HAClient

logger = logging.getLogger(__name__)


class SensorPoller:
    def __init__(self, client: HAClient, interval_seconds: int = 900) -> None:
        self._client = client
        self._interval = interval_seconds
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._sensors: set[str] = set()

    async def add_sensor(self, entity_id: str) -> None:
        self._sensors.add(entity_id)

    async def start(self, callback: Callable[[str, float], Awaitable[None]]) -> None:
        self._running = True
        self._task = asyncio.create_task(self._poll_loop(callback))
        logger.info("Sensor polling started (every %d s)", self._interval)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        logger.info("Sensor polling stopped")

    async def _poll_loop(self, callback: Callable[[str, float], Awaitable[None]]) -> None:
        while self._running:
            await self._poll_once(callback)
            await asyncio.sleep(self._interval)

    async def _poll_once(self, callback: Callable[[str, float], Awaitable[None]]) -> None:
        for entity_id in list(self._sensors):
            value = await self._read_sensor(entity_id)
            if value is not None:
                try:
                    await callback(entity_id, value)
                except Exception:
                    logger.exception("Polling callback error for %s", entity_id)

    async def _read_sensor(self, entity_id: str) -> float | None:
        if not entity_id or not entity_id.strip():
            return None

        data = await self._client.get_state(entity_id.strip())
        if not data:
            return None

        state = data.get("state", "")
        if state in ("unknown", "unavailable", ""):
            return None

        try:
            return float(state)
        except (ValueError, TypeError):
            logger.warning("HA sensor %s: non-numeric state %r", entity_id, state)
            return None
