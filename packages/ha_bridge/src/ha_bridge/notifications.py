import asyncio
import logging
from datetime import datetime, timedelta

from ha_bridge.client import HAClient

logger = logging.getLogger(__name__)

_NOTIFICATION_DOMAIN = "persistent_notification"
_CREATE_SERVICE = "create"
_DISMISS_SERVICE = "dismiss"

_ID_PREFIX = "byrd_health"


def _make_id(slug: str, suffix: str) -> str:
    """Create a per-profile notification ID: byrd_health_{slug}_{suffix}."""
    return f"{_ID_PREFIX}_{slug}_{suffix}"


class HANotifier:
    """Sends persistent notifications via HA API."""

    def __init__(self, client: HAClient):
        self._client = client

    async def send_temp_reminder(self, slug: str, temp_unit: str = "F") -> None:
        unit_sym = "\u00b0F" if temp_unit == "F" else "\u00b0C"
        await self._client.call_service(
            _NOTIFICATION_DOMAIN,
            _CREATE_SERVICE,
            {
                "message": f"Time to take your temperature! {unit_sym}",
                "title": "Byrd Health",
                "notification_id": _make_id(slug, "temp_reminder"),
            },
        )

    async def send_fertile_window_alert(self, slug: str, fertile_start: str, fertile_end: str) -> None:
        await self._client.call_service(
            _NOTIFICATION_DOMAIN,
            _CREATE_SERVICE,
            {
                "message": f"Your fertile window is active ({fertile_start} to {fertile_end}).",
                "title": "Byrd Health",
                "notification_id": _make_id(slug, "fertile_window"),
            },
        )

    async def send_period_prediction(self, slug: str, predicted_date: str) -> None:
        await self._client.call_service(
            _NOTIFICATION_DOMAIN,
            _CREATE_SERVICE,
            {
                "message": f"Your period may start around {predicted_date}.",
                "title": "Byrd Health",
                "notification_id": _make_id(slug, "period_soon"),
            },
        )

    async def send_ovulation_detected(self, slug: str, ovulation_date: str) -> None:
        await self._client.call_service(
            _NOTIFICATION_DOMAIN,
            _CREATE_SERVICE,
            {
                "message": f"Ovulation detected on {ovulation_date}!",
                "title": "Byrd Health",
                "notification_id": _make_id(slug, "ovulation_detected"),
            },
        )

    async def clear_notification(self, notification_id: str) -> None:
        await self._client.call_service(
            _NOTIFICATION_DOMAIN,
            _DISMISS_SERVICE,
            {"notification_id": notification_id},
        )

    async def clear_temp_reminder(self, slug: str) -> None:
        await self.clear_notification(_make_id(slug, "temp_reminder"))


class TempReminderScheduler:
    """Schedules a daily temp reminder notification."""

    def __init__(self, notifier: HANotifier, reminder_time: str, temp_unit: str = "F", profile_slug: str = "default"):
        self._notifier = notifier
        self._reminder_time = reminder_time
        self._temp_unit = temp_unit
        self._slug = profile_slug
        self._task: asyncio.Task[None] | None = None
        self._running = False

    def _seconds_until_next(self) -> float:
        now = datetime.now()
        try:
            hour, minute = map(int, self._reminder_time.split(":"))
        except (ValueError, AttributeError):
            hour, minute = 7, 0
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Temp reminder scheduler started (daily at %s)", self._reminder_time)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Temp reminder scheduler stopped")

    async def _run_loop(self) -> None:
        while self._running:
            delay = self._seconds_until_next()
            logger.debug("Next temp reminder in %.0f seconds", delay)
            try:
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                return
            if self._running:
                await self._notifier.send_temp_reminder(self._slug, self._temp_unit)
