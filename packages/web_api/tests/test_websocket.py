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
                "type": "device_reading",
                "payload": {
                    "profile_slug": "default",
                    "timestamp": "2026-07-25T12:00:00Z",
                    "data": {"sensor.bbt": 97.5},
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
                        "type": "analysis_complete",
                        "payload": {
                            "profile_slug": "default",
                            "timestamp": "2026-07-25T12:00:00Z",
                            "data": {"ovulation_detected": True},
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
                "type": "error",
                "payload": {
                    "profile_slug": "default",
                    "timestamp": "2026-07-25T12:00:00Z",
                    "data": {"code": "TEST_ERROR"},
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
                "type": "device_reading",
                "payload": {
                    "profile_slug": "default",
                    "timestamp": "2026-07-25T12:00:00Z",
                    "data": {"sensor.bbt": 97.5},
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))
            received = ws.receive_json()
            assert "type" in received
            assert "payload" in received
            assert received["type"] in {
                "device_reading",
                "analysis_complete",
                "error",
            }
            payload = received["payload"]
            assert "profile_slug" in payload
            assert "timestamp" in payload
            assert "data" in payload

    def test_valid_message_types(self, ws_client, broker):
        valid_types = {"device_reading", "analysis_complete", "error"}
        for msg_type in valid_types:
            with ws_client.websocket_connect("/api/v1/fertility/ws") as ws:
                message = {
                    "type": msg_type,
                    "payload": {
                        "profile_slug": "default",
                        "timestamp": "2026-07-25T12:00:00Z",
                        "data": {},
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
                "type": "device_reading",
                "payload": {
                    "profile_slug": "default",
                    "timestamp": now_iso,
                    "data": {},
                },
            }
            loop = asyncio.get_event_loop()
            loop.run_until_complete(broker.broadcast(message))
            received = ws.receive_json()
            assert received["payload"]["timestamp"] == now_iso
