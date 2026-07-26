import pytest
from ha_bridge.bridge import HABridge, HABridgeConfig
from ha_bridge.notifications import HANotifier

TEST_SLUG = "test"


async def test_send_temp_reminder_calls_correct_service(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.send_temp_reminder(TEST_SLUG, "F")

    assert len(mock_client.service_calls) == 1
    call = mock_client.service_calls[0]
    assert call["domain"] == "persistent_notification"
    assert call["service"] == "create"
    assert call["data"]["notification_id"] == "byrd_health_test_temp_reminder"
    assert call["data"]["title"] == "Byrd Health"
    assert "temperature" in call["data"]["message"].lower()
    assert "\u00b0F" in call["data"]["message"]


async def test_send_temp_reminder_celsius(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.send_temp_reminder(TEST_SLUG, "C")

    assert "\u00b0C" in mock_client.service_calls[0]["data"]["message"]


async def test_send_fertile_window_alert_with_date_range(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.send_fertile_window_alert(TEST_SLUG, "2026-01-08", "2026-01-16")

    call = mock_client.service_calls[0]
    assert call["domain"] == "persistent_notification"
    assert call["service"] == "create"
    assert call["data"]["notification_id"] == "byrd_health_test_fertile_window"
    assert "fertile window" in call["data"]["message"].lower()
    assert "2026-01-08" in call["data"]["message"]
    assert "2026-01-16" in call["data"]["message"]


async def test_send_period_prediction_with_date(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.send_period_prediction(TEST_SLUG, "2026-02-01")

    call = mock_client.service_calls[0]
    assert call["data"]["notification_id"] == "byrd_health_test_period_soon"
    assert "2026-02-01" in call["data"]["message"]


async def test_send_ovulation_detected_with_date(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.send_ovulation_detected(TEST_SLUG, "2026-01-14")

    call = mock_client.service_calls[0]
    assert call["data"]["notification_id"] == "byrd_health_test_ovulation_detected"
    assert "2026-01-14" in call["data"]["message"]


async def test_notification_ids_are_unique_with_same_slug(mock_client):
    notifier = HANotifier(mock_client)

    await notifier.send_temp_reminder(TEST_SLUG)
    await notifier.send_fertile_window_alert(TEST_SLUG, "2026-01-08", "2026-01-16")
    await notifier.send_period_prediction(TEST_SLUG, "2026-02-01")
    await notifier.send_ovulation_detected(TEST_SLUG, "2026-01-14")

    ids = [c["data"]["notification_id"] for c in mock_client.service_calls]
    assert len(ids) == len(set(ids)), f"Duplicate notification IDs found: {ids}"
    assert set(ids) == {
        "byrd_health_test_temp_reminder",
        "byrd_health_test_fertile_window",
        "byrd_health_test_period_soon",
        "byrd_health_test_ovulation_detected",
    }


async def test_notification_ids_per_profile(mock_client):
    """Different profile slugs produce different notification IDs."""
    notifier = HANotifier(mock_client)

    await notifier.send_temp_reminder("alice")
    await notifier.send_temp_reminder("bob")

    ids = [c["data"]["notification_id"] for c in mock_client.service_calls]
    assert set(ids) == {"byrd_health_alice_temp_reminder", "byrd_health_bob_temp_reminder"}


async def test_clear_notification(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.clear_notification("byrd_health_test_temp_reminder")

    call = mock_client.service_calls[0]
    assert call["domain"] == "persistent_notification"
    assert call["service"] == "dismiss"
    assert call["data"]["notification_id"] == "byrd_health_test_temp_reminder"


async def test_clear_temp_reminder(mock_client):
    notifier = HANotifier(mock_client)
    await notifier.clear_temp_reminder(TEST_SLUG)

    call = mock_client.service_calls[0]
    assert call["service"] == "dismiss"
    assert call["data"]["notification_id"] == "byrd_health_test_temp_reminder"


async def test_fertile_window_notification_on_startup(mock_client):
    config = HABridgeConfig(notify_fertile_window=True)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2099-12-31",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    fertile_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_fertile_window"
    ]
    assert len(fertile_calls) == 1


async def test_fertile_window_notification_suppressed_when_disabled(mock_client):
    config = HABridgeConfig(notify_fertile_window=False)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2099-12-31",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    fertile_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_fertile_window"
    ]
    assert len(fertile_calls) == 0


async def test_ovulation_notification_on_confirmed(mock_client):
    config = HABridgeConfig(notify_ovulation_detected=True)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 16,
        "phase": "luteal",
        "ovulation_date": "2026-01-14",
        "ovulation_confirmed": True,
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    ov_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_ovulation_detected"
    ]
    assert len(ov_calls) == 1


async def test_ovulation_notification_suppressed_when_disabled(mock_client):
    config = HABridgeConfig(notify_ovulation_detected=False)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 16,
        "phase": "luteal",
        "ovulation_date": "2026-01-14",
        "ovulation_confirmed": True,
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    ov_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_ovulation_detected"
    ]
    assert len(ov_calls) == 0


async def test_period_prediction_notification(mock_client):
    config = HABridgeConfig(notify_period_prediction=True)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 25,
        "phase": "luteal",
        "next_period_date": "2026-02-01",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights, "2026-02-01")

    period_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_period_soon"
    ]
    assert len(period_calls) == 1


async def test_period_prediction_suppressed_when_disabled(mock_client):
    config = HABridgeConfig(notify_period_prediction=False)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 25,
        "phase": "luteal",
        "next_period_date": "2026-02-01",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights, "2026-02-01")

    period_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_period_soon"
    ]
    assert len(period_calls) == 0


async def test_no_notification_when_fertile_window_not_active(mock_client):
    config = HABridgeConfig(notify_fertile_window=True)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 5,
        "phase": "follicular",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2020-01-05",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    fertile_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_fertile_window"
    ]
    assert len(fertile_calls) == 0


async def test_all_notifications_disabled(mock_client):
    config = HABridgeConfig(
        notify_fertile_window=False,
        notify_ovulation_detected=False,
        notify_period_prediction=False,
    )
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2099-12-31",
        "ovulation_date": "2026-01-14",
        "ovulation_confirmed": True,
        "next_period_date": "2026-02-01",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights, "2026-02-01")

    assert len(mock_client.service_calls) == 0


async def test_alt_fertile_keys_used_for_notification(mock_client):
    config = HABridgeConfig(notify_fertile_window=True)
    bridge = HABridge(config, mock_client)

    insights = {
        "cycle_day": 10,
        "phase": "follicular",
        "fertile_start": "2020-01-01",
        "fertile_end": "2099-12-31",
    }
    await bridge.publish_insights("alice", "Alice", "F", insights)

    fertile_calls = [
        c for c in mock_client.service_calls
        if c["data"]["notification_id"] == "byrd_health_alice_fertile_window"
    ]
    assert len(fertile_calls) == 1


async def test_default_config_values():
    config = HABridgeConfig()
    assert config.notify_temp_reminder is True
    assert config.notify_temp_reminder_time == "07:00"
    assert config.notify_fertile_window is True
    assert config.notify_period_prediction is True
    assert config.notify_ovulation_detected is True
    assert config.ha_api_timeout == 5.0
