import asyncio

from ha_bridge.bridge import HABridge, HABridgeConfig
from ha_bridge.ingress import IngressMiddleware


async def test_bridge_config_defaults():
    config = HABridgeConfig()
    assert config.temp_unit == "F"
    assert config.ha_sensor_entity == ""
    assert config.poll_interval_seconds == 900


async def test_bridge_publish_delegates(mock_client, sample_insights):
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.publish_insights("alice", "Alice", "F", sample_insights)

    assert len(mock_client.posted_states) == 9
    ids = {s["entity_id"] for s in mock_client.posted_states}
    assert "sensor.bbt_alice_cycle_day" in ids


async def test_bridge_start_polling_adds_sensor(mock_client):
    config = HABridgeConfig(ha_sensor_entity="sensor.temp", poll_interval_seconds=60)
    bridge = HABridge(config, mock_client)

    mock_client._get_state_return = {"state": "98.6"}
    results: list[tuple[str, float]] = []

    async def cb(entity_id: str, value: float) -> None:
        results.append((entity_id, value))

    await bridge.start_polling(cb)
    await asyncio.sleep(0.1)
    await bridge.stop_polling()


async def test_bridge_can_stop_without_starting():
    bridge = HABridge(HABridgeConfig())
    await bridge.stop_polling()


async def test_ingress_middleware_no_ingress_header():
    async def dummy_app(scope, receive, send):
        assert scope["type"] == "http"
        assert scope["path"] == "/api/test"
        assert "script_name" not in scope

    middleware = IngressMiddleware(dummy_app)

    async def receive():
        return {"type": "http.request"}

    events: list[dict] = []

    async def send(event):
        events.append(event)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/test",
        "headers": [],
    }
    await middleware(scope, receive, send)


async def test_ingress_middleware_strips_prefix():
    async def dummy_app(scope, receive, send):
        assert scope["path"] == "/test"
        assert scope["script_name"] == "/hassio/ingress/bbt"

    middleware = IngressMiddleware(dummy_app)

    async def receive():
        return {"type": "http.request"}

    async def send(event):
        pass

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/hassio/ingress/bbt/test",
        "headers": [(b"x-ingress-path", b"/hassio/ingress/bbt")],
    }
    await middleware(scope, receive, send)


async def test_ingress_middleware_path_is_root():
    async def dummy_app(scope, receive, send):
        assert scope["path"] == "/"
        assert scope["script_name"] == "/hassio/ingress/bbt"

    middleware = IngressMiddleware(dummy_app)

    async def receive():
        return {"type": "http.request"}

    async def send(event):
        pass

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/hassio/ingress/bbt",
        "headers": [(b"x-ingress-path", b"/hassio/ingress/bbt")],
    }
    await middleware(scope, receive, send)


async def test_ingress_middleware_non_http_passthrough():
    async def dummy_app(scope, receive, send):
        assert scope["type"] == "websocket"
        assert scope["path"] == "/ws"
        assert "script_name" not in scope

    middleware = IngressMiddleware(dummy_app)

    async def receive():
        return {}

    async def send(event):
        pass

    scope = {
        "type": "websocket",
        "path": "/ws",
        "headers": [(b"x-ingress-path", b"/hassio/ingress/bbt")],
    }
    await middleware(scope, receive, send)


async def test_bridge_register_lovelace_card_new(mock_client):
    mock_client._lovelace_resources = []
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.register_lovelace_card("/local/bbt-card.js")
    assert len(mock_client._create_resource_calls) == 1
    assert mock_client._create_resource_calls[0]["url"] == "/local/bbt-card.js"


async def test_bridge_register_lovelace_card_already_exists(mock_client):
    mock_client._lovelace_resources = [{"id": "1", "url": "/local/bbt-card.js"}]
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.register_lovelace_card("/local/bbt-card.js")
    assert len(mock_client._create_resource_calls) == 0


async def test_bridge_register_lovelace_removes_stale(mock_client):
    stale_url = "https://cdn.jsdelivr.net/gh/kylerpbyrd/bbt-fertility-tracker@main/app/static/js/bbt-card.js"
    mock_client._lovelace_resources = [
        {"id": "1", "url": stale_url},
    ]
    bridge = HABridge(HABridgeConfig(), mock_client)
    await bridge.register_lovelace_card("/local/bbt-card.js")
    assert mock_client._delete_calls == ["1"]
    assert len(mock_client._create_resource_calls) == 1


async def test_bridge_get_ingress_middleware():
    bridge = HABridge(HABridgeConfig())
    app_called = False

    async def dummy_app(scope, receive, send):
        nonlocal app_called
        app_called = True

    mw = bridge.get_ingress_middleware(dummy_app)
    assert isinstance(mw, IngressMiddleware)
