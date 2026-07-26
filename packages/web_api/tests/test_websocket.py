import asyncio
from datetime import UTC

import pytest
from starlette.testclient import TestClient
from web_api.dependencies import set_ws_broker
from web_api.websocket import WebSocketBroker


@pytest.fixture
def broker():
    return WebSocketBroker()


@pytest.fixture
def ws_client(test_app, broker):
    set_ws_broker(broker)
    return TestClient(test_app)


class TestWebSocketConnection:
    def test_connect(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            assert broker.connection_count == 1

    def test_disconnect_cleanup(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            assert broker.connection_count == 1
        assert broker.connection_count == 0

    def test_multiple_connections(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws1:
            assert broker.connection_count == 1
            with ws_client.websocket_connect("/api/v1/fertility/ws") as ws2:
                assert broker.connection_count == 2
                with ws_client.websocket_connect("/api/v1/fertility/ws") as ws3:
                    assert broker.connection_count == 3
                assert broker.connection_count == 2
            assert broker.connection_count == 1
        assert broker.connection_count == 0


class TestWebSocketBroadcast:
    def test_broadcast_to_single_client(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            message = {
                "version": 1,
                "type": "device_reading",
                "timestamp": "2026-07-25T12:00:00Z",
                "payload": {
                    "profile_slug": "default",
                    "device_id": "sensor.bbt",
                    "device_type": "ha_sensor",
                    "temperature": 97.5,
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))
            received = ws.receive_json()
            assert received == message

    def test_broadcast_to_multiple_clients(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws1:
            with ws_client.websocket_connect("/api/v1/fertility/ws") as ws2:
                with ws_client.websocket_connect("/api/v1/fertility/ws") as ws3:
                    message = {
                        "version": 1,
                        "type": "analysis_complete",
                        "timestamp": "2026-07-25T12:00:00Z",
                        "payload": {
                            "profile_slug": "default",
                        },
                    }
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(broker.broadcast(message))
                    assert ws1.receive_json() == message
                    assert ws2.receive_json() == message
                    assert ws3.receive_json() == message

    def test_broadcast_skips_dead_connections(self, ws_client, broker):
        class DeadSocket:
            async def send_json(self, data):
                raise RuntimeError("simulated dead connection")

        dead = DeadSocket()
        broker._connections.add(dead)

        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            assert broker.connection_count == 2

            message = {
                "version": 1,
                "type": "error",
                "timestamp": "2026-07-25T12:00:00Z",
                "payload": {
                    "code": "TEST_ERROR",
                    "message": "Test error",
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))

            assert broker.connection_count == 1
            received = ws.receive_json()
            assert received == message


class TestMessageProtocol:
    def test_message_has_required_fields(self, ws_client, broker):
        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            message = {
                "version": 1,
                "type": "device_reading",
                "timestamp": "2026-07-25T12:00:00Z",
                "payload": {
                    "profile_slug": "default",
                    "device_id": "sensor.bbt",
                    "device_type": "ha_sensor",
                    "temperature": 97.5,
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))
            received = ws.receive_json()
            assert "version" in received
            assert "type" in received
            assert "timestamp" in received
            assert "payload" in received
            assert received["type"] in {
                "device_reading",
                "analysis_complete",
                "error",
            }
            assert received["version"] == 1
            payload = received["payload"]
            assert "profile_slug" in payload
            assert "device_id" in payload
            assert "device_type" in payload
            assert "temperature" in payload

    def test_valid_message_types(self, ws_client, broker):
        valid_types = {"device_reading", "analysis_complete", "error"}
        for msg_type in valid_types:
            with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
                message = {
                    "version": 1,
                    "type": msg_type,
                    "timestamp": "2026-07-25T12:00:00Z",
                    "payload": {
                        "profile_slug": "default",
                    },
                }
                loop = asyncio.get_event_loop()
                loop.run_until_complete(broker.broadcast(message))
                received = ws.receive_json()
                assert received["type"] == msg_type

    def test_payload_timestamp_is_iso8601(self, ws_client, broker):
        from datetime import datetime

        with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
            now_iso = datetime.now(UTC).isoformat()
            message = {
                "version": 1,
                "type": "device_reading",
                "timestamp": now_iso,
                "payload": {
                    "profile_slug": "default",
                    "device_id": "sensor.bbt",
                    "device_type": "ha_sensor",
                    "temperature": 97.5,
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))
            received = ws.receive_json()
            assert received["timestamp"] == now_iso


class TestMakeMessage:
    def test_correct_envelope(self):
        from web_api.websocket import make_message

        msg = make_message("device_reading", {"temperature": 97.5})
        assert msg["version"] == 1
        assert msg["type"] == "device_reading"
        assert "timestamp" in msg
        assert msg["payload"] == {"temperature": 97.5}

    def test_correct_types(self):
        from web_api.websocket import make_message

        msg = make_message("analysis_complete", {"profile_slug": "default"})
        assert isinstance(msg["version"], int)
        assert isinstance(msg["type"], str)
        assert isinstance(msg["timestamp"], str)
        assert isinstance(msg["payload"], dict)

    def test_timestamp_is_iso8601(self):
        from datetime import datetime

        from web_api.websocket import make_message

        msg = make_message("device_reading", {})
        ts = msg["timestamp"]

        parsed = datetime.fromisoformat(ts)
        assert parsed.tzinfo is not None
        assert "+" in ts or "Z" in ts or ts.endswith(":00")
