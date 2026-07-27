from ha_bridge.bridge import HABridge, HABridgeConfig
from ha_bridge.entities import (
    publish_last_medication_entity,
    publish_pregnancy_entities,
    publish_profile_entities,
)


async def test_publish_all_nine_entities(mock_client):
    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "last_temp": 97.832,
        "ovulation_confirmed": True,
        "ovulation_date": "2026-01-14",
        "fertile_start_date": "2026-01-01",
        "fertile_end_date": "2026-12-31",
        "luteal_length": 14,
        "avg_cycle_length": 28,
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights, "2026-02-01")

    assert len(mock_client.posted_states) == 9

    ids = {s["entity_id"] for s in mock_client.posted_states}
    assert ids == {
        "sensor.bbt_alice_cycle_day",
        "sensor.bbt_alice_cycle_phase",
        "sensor.bbt_alice_last_temp",
        "binary_sensor.bbt_alice_fertile_window",
        "binary_sensor.bbt_alice_ovulation_confirmed",
        "sensor.bbt_alice_ovulation_date",
        "sensor.bbt_alice_next_period_date",
        "sensor.bbt_alice_luteal_length",
        "sensor.bbt_alice_avg_cycle_length",
    }


async def test_entity_states_correct(mock_client):
    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "last_temp": 97.83,
        "ovulation_confirmed": True,
        "ovulation_date": "2026-01-14",
        "fertile_start_date": "2026-01-01",
        "fertile_end_date": "2026-12-31",
        "luteal_length": 14,
        "avg_cycle_length": 28,
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights, "2026-02-01")

    by_id = {s["entity_id"]: s for s in mock_client.posted_states}

    assert by_id["sensor.bbt_alice_cycle_day"]["state"] == "14"
    assert by_id["sensor.bbt_alice_cycle_day"]["attributes"]["unit_of_measurement"] == "days"

    assert by_id["sensor.bbt_alice_cycle_phase"]["state"] == "luteal"
    assert by_id["sensor.bbt_alice_cycle_phase"]["attributes"]["friendly_name"] == "BBT Alice Cycle Phase"

    assert by_id["sensor.bbt_alice_last_temp"]["state"] == "97.83"
    assert by_id["sensor.bbt_alice_last_temp"]["attributes"]["unit_of_measurement"] == "°F"
    assert by_id["sensor.bbt_alice_last_temp"]["attributes"]["device_class"] == "temperature"

    assert by_id["binary_sensor.bbt_alice_fertile_window"]["state"] == "on"
    assert by_id["binary_sensor.bbt_alice_fertile_window"]["attributes"]["device_class"] == "presence"

    assert by_id["binary_sensor.bbt_alice_ovulation_confirmed"]["state"] == "on"

    assert by_id["sensor.bbt_alice_ovulation_date"]["state"] == "2026-01-14"
    assert by_id["sensor.bbt_alice_ovulation_date"]["attributes"]["device_class"] == "date"

    assert by_id["sensor.bbt_alice_next_period_date"]["state"] == "2026-02-01"

    assert by_id["sensor.bbt_alice_luteal_length"]["state"] == "14"
    assert by_id["sensor.bbt_alice_luteal_length"]["attributes"]["unit_of_measurement"] == "days"

    assert by_id["sensor.bbt_alice_avg_cycle_length"]["state"] == "28"


async def test_conditional_entities_omitted_when_none(mock_client):
    insights = {
        "cycle_day": 1,
        "phase": "follicular",
    }
    await publish_profile_entities(mock_client, "bob", "Bob", "C", insights)

    ids = {s["entity_id"] for s in mock_client.posted_states}
    assert "sensor.bbt_bob_last_temp" not in ids
    assert "sensor.bbt_bob_luteal_length" not in ids
    assert "sensor.bbt_bob_avg_cycle_length" not in ids
    assert len(mock_client.posted_states) == 6


async def test_fertile_window_off_when_outside_range(mock_client):
    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2020-01-05",
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    entity = "binary_sensor.bbt_alice_fertile_window"
    fw = next(s for s in mock_client.posted_states if s["entity_id"] == entity)
    assert fw["state"] == "off"


async def test_fertile_window_on_when_in_range(mock_client):
    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "fertile_start_date": "2020-01-01",
        "fertile_end_date": "2099-12-31",
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    entity = "binary_sensor.bbt_alice_fertile_window"
    fw = next(s for s in mock_client.posted_states if s["entity_id"] == entity)
    assert fw["state"] == "on"


async def test_none_values_stripped_from_attributes(mock_client):
    insights = {
        "cycle_day": 10,
        "phase": "follicular",
        "last_temp": 97.5,
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    last_temp = next(s for s in mock_client.posted_states if s["entity_id"] == "sensor.bbt_alice_last_temp")
    assert None not in last_temp["attributes"].values()


async def test_next_period_defaults_to_none(mock_client):
    insights = {"cycle_day": 5, "phase": "follicular"}
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    npd = next(s for s in mock_client.posted_states if s["entity_id"] == "sensor.bbt_alice_next_period_date")
    assert npd["state"] == "none"


async def test_celsius_temp_unit(mock_client):
    insights = {"cycle_day": 10, "phase": "luteal", "last_temp": 36.5}
    await publish_profile_entities(mock_client, "alice", "Alice", "C", insights)

    lt = next(s for s in mock_client.posted_states if s["entity_id"] == "sensor.bbt_alice_last_temp")
    assert lt["attributes"]["unit_of_measurement"] == "°C"


async def test_temp_rounded_to_two_decimals(mock_client):
    insights = {"cycle_day": 10, "phase": "luteal", "last_temp": 97.12345}
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    lt = next(s for s in mock_client.posted_states if s["entity_id"] == "sensor.bbt_alice_last_temp")
    assert lt["state"] == "97.12"


async def test_ovulation_confirmed_false(mock_client):
    insights = {"cycle_day": 10, "phase": "follicular", "ovulation_confirmed": False}
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    entity = "binary_sensor.bbt_alice_ovulation_confirmed"
    oc = next(s for s in mock_client.posted_states if s["entity_id"] == entity)
    assert oc["state"] == "off"


async def test_invalid_fertile_date_handled_gracefully(mock_client):
    insights = {
        "cycle_day": 10,
        "phase": "follicular",
        "fertile_start_date": "not-a-date",
        "fertile_end_date": "also-not-a-date",
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    entity = "binary_sensor.bbt_alice_fertile_window"
    fw = next(s for s in mock_client.posted_states if s["entity_id"] == entity)
    assert fw["state"] == "off"


async def test_fertile_start_end_alt_keys(mock_client):
    insights = {
        "cycle_day": 10,
        "phase": "follicular",
        "fertile_start": "2020-01-01",
        "fertile_end": "2099-12-31",
    }
    await publish_profile_entities(mock_client, "alice", "Alice", "F", insights)

    entity = "binary_sensor.bbt_alice_fertile_window"
    fw = next(s for s in mock_client.posted_states if s["entity_id"] == entity)
    assert fw["state"] == "on"


async def test_bridge_publish_insights_delegates(mock_client, sample_insights):
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.publish_insights("alice", "Alice", "F", sample_insights, "2026-02-01")

    assert len(mock_client.posted_states) == 15


async def test_pregnancy_entities_published_when_active(mock_client):
    pregnancy_data = {
        "is_active": True,
        "current_week": 20,
        "trimester": 2,
        "due_date": "2026-12-15",
        "days_remaining": 142,
    }
    await publish_pregnancy_entities(mock_client, "alice", "Alice", pregnancy_data)

    assert len(mock_client.posted_states) == 5

    ids = {s["entity_id"] for s in mock_client.posted_states}
    assert ids == {
        "sensor.bbt_alice_pregnancy_week",
        "sensor.bbt_alice_pregnancy_trimester",
        "sensor.bbt_alice_pregnancy_due_date",
        "sensor.bbt_alice_pregnancy_days_left",
        "binary_sensor.bbt_alice_pregnancy_active",
    }


async def test_pregnancy_entities_have_correct_values(mock_client):
    pregnancy_data = {
        "is_active": True,
        "current_week": 20,
        "trimester": 2,
        "due_date": "2026-12-15",
        "days_remaining": 142,
    }
    await publish_pregnancy_entities(mock_client, "alice", "Alice", pregnancy_data)

    by_id = {s["entity_id"]: s for s in mock_client.posted_states}

    assert by_id["sensor.bbt_alice_pregnancy_week"]["state"] == "20"
    assert by_id["sensor.bbt_alice_pregnancy_week"]["attributes"]["unit_of_measurement"] == "weeks"

    assert by_id["sensor.bbt_alice_pregnancy_trimester"]["state"] == "2"

    assert by_id["sensor.bbt_alice_pregnancy_due_date"]["state"] == "2026-12-15"
    assert by_id["sensor.bbt_alice_pregnancy_due_date"]["attributes"]["device_class"] == "date"

    assert by_id["sensor.bbt_alice_pregnancy_days_left"]["state"] == "142"
    assert by_id["sensor.bbt_alice_pregnancy_days_left"]["attributes"]["unit_of_measurement"] == "days"

    assert by_id["binary_sensor.bbt_alice_pregnancy_active"]["state"] == "on"
    assert by_id["binary_sensor.bbt_alice_pregnancy_active"]["attributes"]["device_class"] == "presence"


async def test_pregnancy_entities_unavailable_when_inactive(mock_client):
    await publish_pregnancy_entities(mock_client, "alice", "Alice", None)

    for s in mock_client.posted_states:
        entity_id = s["entity_id"]
        if "pregnancy_active" in entity_id:
            assert s["state"] == "off"
        else:
            assert s["state"] == "unavailable"


async def test_pregnancy_entities_unavailable_when_not_active_flag(mock_client):
    pregnancy_data = {"is_active": False}
    await publish_pregnancy_entities(mock_client, "alice", "Alice", pregnancy_data)

    for s in mock_client.posted_states:
        entity_id = s["entity_id"]
        if "pregnancy_active" in entity_id:
            assert s["state"] == "off"
        else:
            assert s["state"] == "unavailable"


async def test_medication_entity_shows_last_medication(mock_client):
    medication_data = {
        "name": "Aspirin",
        "taken_at": "2026-07-26T08:00:00",
        "dosage": "81mg",
    }
    await publish_last_medication_entity(mock_client, "alice", "Alice", medication_data)

    assert len(mock_client.posted_states) == 1

    med = mock_client.posted_states[0]
    assert med["entity_id"] == "sensor.bbt_alice_last_medication"
    assert med["state"] == "Aspirin"
    assert med["attributes"]["medication_name"] == "Aspirin"
    assert med["attributes"]["taken_at"] == "2026-07-26T08:00:00"
    assert med["attributes"]["dosage"] == "81mg"
    assert med["attributes"]["friendly_name"] == "BBT Alice Last Medication"


async def test_medication_entity_unavailable_when_no_data(mock_client):
    await publish_last_medication_entity(mock_client, "alice", "Alice", None)

    assert len(mock_client.posted_states) == 1
    med = mock_client.posted_states[0]
    assert med["entity_id"] == "sensor.bbt_alice_last_medication"
    assert med["state"] == "unavailable"


async def test_bridge_routes_pregnancy_and_medication_from_insights(mock_client):
    insights = {
        "cycle_day": 14,
        "phase": "luteal",
        "pregnancy": {
            "is_active": True,
            "current_week": 12,
            "trimester": 1,
            "due_date": "2027-02-10",
            "days_remaining": 199,
        },
        "last_medication": {
            "name": "Prenatal Vitamin",
            "taken_at": "2026-07-26T09:00:00",
            "dosage": "1 tablet",
        },
    }
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.publish_insights("alice", "Alice", "F", insights)

    by_id = {s["entity_id"]: s for s in mock_client.posted_states}
    assert "sensor.bbt_alice_pregnancy_week" in by_id
    assert by_id["sensor.bbt_alice_pregnancy_week"]["state"] == "12"
    assert "binary_sensor.bbt_alice_pregnancy_active" in by_id
    assert by_id["binary_sensor.bbt_alice_pregnancy_active"]["state"] == "on"
    assert "sensor.bbt_alice_last_medication" in by_id
    assert by_id["sensor.bbt_alice_last_medication"]["state"] == "Prenatal Vitamin"
