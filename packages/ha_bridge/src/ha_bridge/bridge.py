import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from ha_bridge.client import HAClient
from ha_bridge.entities import publish_profile_entities
from ha_bridge.ingress import IngressMiddleware
from ha_bridge.poller import SensorPoller

logger = logging.getLogger(__name__)


@dataclass
class HABridgeConfig:
    temp_unit: str = "F"
    ha_sensor_entity: str = ""
    poll_interval_seconds: int = 900


class HABridge:
    def __init__(self, config: HABridgeConfig, client: HAClient | None = None) -> None:
        self._config = config
        self._client = client or HAClient()
        self._poller = SensorPoller(self._client, config.poll_interval_seconds)

    async def publish_insights(
        self,
        slug: str,
        name: str,
        temp_unit: str,
        insights: dict[str, Any],
        next_period: str | None = None,
    ) -> None:
        await publish_profile_entities(
            client=self._client,
            slug=slug,
            name=name,
            temp_unit=temp_unit,
            insights=insights,
            next_period=next_period,
        )

    async def start_polling(self, on_reading: Callable[[str, float], Awaitable[None]]) -> None:
        if self._config.ha_sensor_entity:
            await self._poller.add_sensor(self._config.ha_sensor_entity)
        await self._poller.start(on_reading)

    async def stop_polling(self) -> None:
        await self._poller.stop()

    async def publish_entities(self, profile_slug: str) -> None:
        logger.warning("publish_entities(%s) called without profile data; use publish_insights for now", profile_slug)

    async def publish_all_profiles(self) -> None:
        logger.warning("publish_all_profiles() called without data access; publish from lifespan for now")

    async def startup(self) -> None:
        logger.debug("HABridge startup (noop)")

    async def shutdown(self) -> None:
        await self.stop_polling()

    def get_ingress_middleware(self, app: object) -> IngressMiddleware:
        return IngressMiddleware(app)  # type: ignore[arg-type]

    async def register_lovelace_card(self, card_url: str = "/local/bbt-card.js") -> None:
        old_card_urls = [
            "https://cdn.jsdelivr.net/gh/kylerpbyrd/bbt-fertility-tracker@main/app/static/js/bbt-card.js",
            "/hassio/ingress/bbt_fertility_tracker/bbt-card.js",
        ]

        resources = await self._client.get_lovelace_resources()
        if resources is None:
            logger.warning("Lovelace resources API not available (YAML mode?)")
            return

        for r in resources:
            if r.get("url") in old_card_urls:
                rid = r.get("id")
                if rid is not None:
                    await self._client.delete_lovelace_resource(str(rid))
                    logger.info("Removed old Lovelace resource: %s", r.get("url"))

        resources = await self._client.get_lovelace_resources() or []
        if any(r.get("url") == card_url for r in resources):
            logger.debug("Lovelace card already registered")
            return

        result = await self._client.create_lovelace_resource(card_url)
        if result:
            logger.info("Lovelace card registered at %s", card_url)
        else:
            logger.warning("Could not register Lovelace card resource")
