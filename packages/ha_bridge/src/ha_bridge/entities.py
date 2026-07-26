import contextlib
import logging
from datetime import date
from typing import Any

from ha_bridge.client import HAClient

logger = logging.getLogger(__name__)


async def publish_profile_entities(
    client: HAClient,
    slug: str,
    name: str,
    temp_unit: str,
    insights: dict[str, Any],
    next_period: str | None = None,
) -> None:
    cycle_day = insights.get("cycle_day", "unknown")
    phase = insights.get("phase", "unknown")
    last_temp = insights.get("last_temp")
    ov_confirmed = bool(insights.get("ovulation_confirmed"))
    ov_date = insights.get("ovulation_date") or "none"
    luteal = insights.get("luteal_length")
    avg_cycle = insights.get("avg_cycle_length")

    in_fertile = False
    fertile_start = insights.get("fertile_start_date") or insights.get("fertile_start")
    fertile_end = insights.get("fertile_end_date") or insights.get("fertile_end")
    with contextlib.suppress(ValueError):
        if fertile_start and fertile_end:
            in_fertile = (
                date.fromisoformat(fertile_start)
                <= date.today()
                <= date.fromisoformat(fertile_end)
            )

    entities: list[tuple[str, str, dict[str, Any]]] = [
        (
            f"sensor.bbt_{slug}_cycle_day",
            str(cycle_day),
            {
                "friendly_name": f"BBT {name} Cycle Day",
                "unit_of_measurement": "days",
                "icon": "mdi:calendar-today",
                "unique_id": f"byrd_health_{slug}_cycle_day",
            },
        ),
        (
            f"sensor.bbt_{slug}_cycle_phase",
            phase,
            {
                "friendly_name": f"BBT {name} Cycle Phase",
                "icon": "mdi:water-circle",
                "unique_id": f"byrd_health_{slug}_cycle_phase",
            },
        ),
        (
            f"binary_sensor.bbt_{slug}_fertile_window",
            "on" if in_fertile else "off",
            {
                "friendly_name": f"BBT {name} Fertile Window",
                "icon": "mdi:seed",
                "device_class": "presence",
                "unique_id": f"byrd_health_{slug}_fertile_window",
            },
        ),
        (
            f"binary_sensor.bbt_{slug}_ovulation_confirmed",
            "on" if ov_confirmed else "off",
            {
                "friendly_name": f"BBT {name} Ovulation Confirmed",
                "icon": "mdi:check-circle",
                "device_class": "presence",
                "unique_id": f"byrd_health_{slug}_ovulation_confirmed",
            },
        ),
        (
            f"sensor.bbt_{slug}_ovulation_date",
            ov_date,
            {
                "friendly_name": f"BBT {name} Ovulation Date",
                "icon": "mdi:calendar-star",
                "device_class": "date",
                "unique_id": f"byrd_health_{slug}_ovulation_date",
            },
        ),
        (
            f"sensor.bbt_{slug}_next_period_date",
            next_period or "none",
            {
                "friendly_name": f"BBT {name} Next Period Date",
                "icon": "mdi:calendar-arrow-right",
                "device_class": "date",
                "unique_id": f"byrd_health_{slug}_next_period_date",
            },
        ),
    ]

    if last_temp is not None:
        entities.append((
            f"sensor.bbt_{slug}_last_temp",
            str(round(float(last_temp), 2)),
            {
                "friendly_name": f"BBT {name} Last Temperature",
                "unit_of_measurement": f"°{temp_unit}",
                "icon": "mdi:thermometer",
                "device_class": "temperature",
                "unique_id": f"byrd_health_{slug}_last_temp",
            },
        ))

    if luteal is not None:
        entities.append((
            f"sensor.bbt_{slug}_luteal_length",
            str(luteal),
            {
                "friendly_name": f"BBT {name} Luteal Length",
                "unit_of_measurement": "days",
                "icon": "mdi:timer-sand",
                "unique_id": f"byrd_health_{slug}_luteal_length",
            },
        ))

    if avg_cycle is not None:
        entities.append((
            f"sensor.bbt_{slug}_avg_cycle_length",
            str(avg_cycle),
            {
                "friendly_name": f"BBT {name} Avg Cycle Length",
                "unit_of_measurement": "days",
                "icon": "mdi:chart-timeline-variant",
                "unique_id": f"byrd_health_{slug}_avg_cycle_length",
            },
        ))

    for entity_id, state, attrs in entities:
        await client.post_state(entity_id, state, attrs)
        logger.debug("Published %s = %s", entity_id, state)
