import asyncio
import datetime
from datetime import timezone

import pytest
from starlette.testclient import TestClient

from device_adapters.registry import DeviceRegistry
from web_api.dependencies import set_device_registry, set_ws_broker
from web_api.websocket import WebSocketBroker


class MockAdapter:
    def __init__(self, device_id: str, device_type: str, connected: bool = True):
        self._device_id = device_id
        self._device_type = device_type
        self._connected = connected
        self._temperature = 97.5
        self.connect_called = False
        self.disconnect_called = False

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> str:
        return self._device_type

    async def connect(self) -> None:
        self.connect_called = True
        self._connected = True

    async def disconnect(self) -> None:
        self.disconnect_called = True
        self._connected = False

    async def read_temperature(self) -> float | None:
        return self._temperature

    async def is_connected(self) -> bool:
        return self._connected


@pytest.fixture
def registry():
    return DeviceRegistry()


@pytest.fixture
def broker():
    return WebSocketBroker()


@pytest.fixture
def device_client(test_app, registry, broker):
    set_device_registry(registry)
    set_ws_broker(broker)
    return TestClient(test_app)


class TestListDevices:
    def test_empty_registry(self, device_client):
        response = device_client.get("/api/v1/fertility/devices/")
        assert response.status_code == 200
        data = response.json()
        assert data["devices"] == []

    def test_lists_registered_adapters(self, device_client, registry):
        adapter = MockAdapter("sensor.bbt", "ha_sensor")
        registry.register(adapter)

        response = device_client.get("/api/v1/fertility/devices/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["devices"]) == 1
        assert data["devices"][0]["device_id"] == "sensor.bbt"
        assert data["devices"][0]["device_type"] == "ha_sensor"

    def test_lists_multiple_adapters(self, device_client, registry):
        registry.register(MockAdapter("sensor.bbt", "ha_sensor"))
        registry.register(MockAdapter("sensor.temp2", "esphome"))
        registry.register(MockAdapter("BLE_thermometer", "bluetooth"))

        response = device_client.get("/api/v1/fertility/devices/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["devices"]) == 3


class TestDeviceRead:
    def test_read_no_registry(self, device_client, registry):
        set_device_registry(None)
        response = device_client.post("/api/v1/fertility/devices/read")
        assert response.status_code == 503

    def test_read_empty_registry(self, device_client, registry):
        response = device_client.post("/api/v1/fertility/devices/read")
        assert response.status_code == 200
        data = response.json()
        assert data["readings"] == {}

    def test_read_all_connected(self, device_client, registry):
        registry.register(MockAdapter("sensor.bbt", "ha_sensor", connected=True))
        registry.register(MockAdapter("sensor.temp2", "esphome", connected=True))

        response = device_client.post("/api/v1/fertility/devices/read")
        assert response.status_code == 200
        data = response.json()
        assert len(data["readings"]) == 2
        assert data["readings"]["sensor.bbt"] == 97.5
        assert data["readings"]["sensor.temp2"] == 97.5

    def test_read_skips_disconnected(self, device_client, registry):
        registry.register(MockAdapter("sensor.bbt", "ha_sensor", connected=True))
        registry.register(MockAdapter("sensor.offline", "esphome", connected=False))

        response = device_client.post("/api/v1/fertility/devices/read")
        assert response.status_code == 200
        data = response.json()
        assert len(data["readings"]) == 1
        assert data["readings"]["sensor.bbt"] == 97.5
        assert "sensor.offline" not in data["readings"]

    def test_read_broadcasts_result(self, device_client, registry, broker):
        registry.register(MockAdapter("sensor.bbt", "ha_sensor", connected=True))

        with device_client.websocket_connect("/api/v1/fertility/ws") as ws:
            response = device_client.post("/api/v1/fertility/devices/read")
            assert response.status_code == 200

            msg = ws.receive_json()
            assert msg["type"] == "device_reading"
            assert msg["payload"]["profile_slug"] == "default"
            assert "timestamp" in msg["payload"]
            assert msg["payload"]["data"]["sensor.bbt"] == 97.5


class TestDeviceStatus:
    def test_status_no_registry(self, device_client, registry):
        set_device_registry(None)
        response = device_client.get("/api/v1/fertility/devices/sensor.bbt/status")
        assert response.status_code == 503

    def test_status_not_found(self, device_client, registry):
        response = device_client.get("/api/v1/fertility/devices/nonexistent/status")
        assert response.status_code == 404

    def test_status_connected(self, device_client, registry):
        registry.register(MockAdapter("sensor.bbt", "ha_sensor", connected=True))

        response = device_client.get("/api/v1/fertility/devices/sensor.bbt/status")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "sensor.bbt"
        assert data["device_type"] == "ha_sensor"
        assert data["connected"] is True

    def test_status_disconnected(self, device_client, registry):
        registry.register(MockAdapter("sensor.offline", "esphome", connected=False))

        response = device_client.get("/api/v1/fertility/devices/sensor.offline/status")
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False
