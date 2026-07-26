import contextlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from ha_bridge.client import HAClient
from ha_bridge.entities import publish_profile_entities
from ha_bridge.ingress import IngressMiddleware
from ha_bridge.notifications import HANotifier, TempReminderScheduler
from ha_bridge.poller import SensorPoller

logger = logging.getLogger(__name__)


@dataclass
class HABridgeConfig:
    temp_unit: str = "F"
    ha_sensor_entity: str = ""
    poll_interval_seconds: int = 900
    ha_api_timeout: float = 5.0
    notify_temp_reminder: bool = True
    notify_temp_reminder_time: str = "07:00"
    notify_fertile_window: bool = True
    notify_period_prediction: bool = True
    notify_ovulation_detected: bool = True


class HABridge:
    def __init__(self, config: HABridgeConfig, client: HAClient | None = None) -> None:
        self._config = config
        self._client = client or HAClient(timeout=config.ha_api_timeout)
        self._poller = SensorPoller(self._client, config.poll_interval_seconds)
        self._notifier = HANotifier(self._client)
        self._temp_scheduler = TempReminderScheduler(
            self._notifier,
            config.notify_temp_reminder_time,
            config.temp_unit,
        )

    @property
    def client(self) -> HAClient:
        """Expose the HAClient for device adapter registration."""
        return self._client

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
        await self._check_notifications(slug, insights)

    async def start_polling(self, on_reading: Callable[[str, float], Awaitable[None]]) -> None:
        if self._config.ha_sensor_entity:
            await self._poller.add_sensor(self._config.ha_sensor_entity)
        await self._poller.start(on_reading)

    async def stop_polling(self) -> None:
        await self._poller.stop()

    async def publish_entities(self, profile_slug: str) -> None:
        """Publish entities for a profile (delegates to publish_insights when data available)."""
        logger.debug("publish_entities(%s) — use publish_insights with full data for entity publishing", profile_slug)

    async def publish_all_profiles(self) -> None:
        """Publish entities for all profiles (use app lifespan for batch publishing)."""
        logger.debug("publish_all_profiles() — batch publishing handled by app lifespan")

    async def start_temp_reminder(self) -> None:
        if self._config.notify_temp_reminder:
            await self._temp_scheduler.start()

    async def stop_temp_reminder(self) -> None:
        await self._temp_scheduler.stop()

    async def startup(self) -> None:
        logger.debug("HABridge startup")
        await self.start_temp_reminder()

    async def shutdown(self) -> None:
        await self.stop_temp_reminder()
        await self.stop_polling()

    async def _check_notifications(self, slug: str, insights: dict[str, Any]) -> None:
        try:
            if self._config.notify_fertile_window:
                fertile_start = insights.get("fertile_start_date") or insights.get("fertile_start")
                fertile_end = insights.get("fertile_end_date") or insights.get("fertile_end")
                if fertile_start and fertile_end:
                    with contextlib.suppress(ValueError):
                        today = date.today()
                        start = date.fromisoformat(fertile_start)
                        end = date.fromisoformat(fertile_end)
                        if start <= today <= end:
                            await self._notifier.send_fertile_window_alert(slug, fertile_start, fertile_end)

            if self._config.notify_ovulation_detected:
                ov_date = insights.get("ovulation_date")
                ov_confirmed = insights.get("ovulation_confirmed")
                if ov_date and ov_confirmed:
                    await self._notifier.send_ovulation_detected(slug, ov_date)

            if self._config.notify_period_prediction:
                next_period = insights.get("next_period_date")
                if next_period:
                    await self._notifier.send_period_prediction(slug, next_period)
        except Exception:
            logger.exception("Failed to send HA notifications")

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

    async def register_dashboard_card(self, card_filename: str = "ha-card.js") -> bool:
        ingress_url = await self._client.get_ingress_url()
        if ingress_url:
            card_url = f"{ingress_url.rstrip('/')}/{card_filename}"
        else:
            card_url = f"/local/{card_filename}"
            logger.warning(
                "Could not discover ingress URL; registering as %s. "
                "Update manually in HA if the card fails to load.",
                card_url,
            )

        await self.register_lovelace_card(card_url)
        return True
