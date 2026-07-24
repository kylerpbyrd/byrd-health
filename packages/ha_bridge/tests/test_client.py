from ha_bridge.client import HAClient


async def test_request_returns_json_on_success():
    client = HAClient(token="fake-token")
    await client.close()


async def test_request_returns_none_when_no_token():
    client = HAClient(token="")
    result = await client._request("GET", "/states/test.entity")
    assert result is None
    await client.close()


async def test_post_state_returns_true_on_success(mock_client):
    result = await mock_client.post_state("sensor.test", "42", {"unit": "°F"})
    assert result is True
    assert len(mock_client.posted_states) == 1
    assert mock_client.posted_states[0]["entity_id"] == "sensor.test"


async def test_get_state_returns_none_for_unset():
    client = HAClient(token="fake-token")
    result = await client.get_state("sensor.test")
    assert result is None
    await client.close()


async def test_get_lovelace_resources_returns_list(mock_client):
    mock_client._lovelace_resources = []
    result = await mock_client.get_lovelace_resources()
    assert result == []


async def test_create_lovelace_resource(mock_client):
    result = await mock_client.create_lovelace_resource("/local/test.js")
    assert result is True
    assert mock_client._create_resource_calls == [{"url": "/local/test.js", "res_type": "module"}]


async def test_delete_lovelace_resource(mock_client):
    result = await mock_client.delete_lovelace_resource("abc123")
    assert result is True
    assert mock_client._delete_calls == ["abc123"]


async def test_none_attributes_stripped(mock_client):
    await mock_client.post_state("sensor.test", "42", {"good": 1, "bad": None})
    assert "bad" not in mock_client.posted_states[0]["attributes"]
