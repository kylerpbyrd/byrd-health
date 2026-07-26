from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from device_adapters.adapters.bluetooth import (
    BluetoothAdapter,
    _parse_ieee11073_float,
)
from device_adapters.protocol import DeviceAdapter


@pytest.fixture
def adapter() -> BluetoothAdapter:
    return BluetoothAdapter("00:11:22:33:44:55")


# ---------------------------------------------------------------------------
# IEEE 11073 float parsing
# ---------------------------------------------------------------------------


def test_parse_ieee11073_float_standard() -> None:
    mantissa = 3660
    exponent = -2
    data = b"".join(
        [
            mantissa.to_bytes(3, byteorder="little", signed=True),
            exponent.to_bytes(1, byteorder="little", signed=True),
        ]
    )
    result = _parse_ieee11073_float(data)
    assert round(result, 1) == 36.6


def test_parse_ieee11073_float_low_temperature() -> None:
    mantissa = 2772
    exponent = -2
    data = b"".join(
        [
            mantissa.to_bytes(3, byteorder="little", signed=True),
            exponent.to_bytes(1, byteorder="little", signed=True),
        ]
    )
    result = _parse_ieee11073_float(data)
    assert round(result, 2) == 27.72


def test_parse_ieee11073_float_negative_exponent() -> None:
    mantissa = 820
    exponent = -1
    data = b"".join(
        [
            mantissa.to_bytes(3, byteorder="little", signed=True),
            exponent.to_bytes(1, byteorder="little", signed=True),
        ]
    )
    result = _parse_ieee11073_float(data)
    assert round(result, 2) == 82.0


def test_parse_ieee11073_float_invalid_length() -> None:
    with pytest.raises(ValueError, match="requires 4 bytes"):
        _parse_ieee11073_float(b"\x01\x02\x03")


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_bluetooth_adapter_implements_protocol(adapter: BluetoothAdapter) -> None:
    assert isinstance(adapter, DeviceAdapter)


def test_device_type_returns_bluetooth(adapter: BluetoothAdapter) -> None:
    assert adapter.device_type == "bluetooth"


def test_device_id_matches_address() -> None:
    adapter = BluetoothAdapter("AA:BB:CC:DD:EE:FF")
    assert adapter.device_id == "ble_AA_BB_CC_DD_EE_FF"


def test_device_id_custom() -> None:
    adapter = BluetoothAdapter("00:00:00:00:00:00", device_id="my_thermometer")
    assert adapter.device_id == "my_thermometer"


# ---------------------------------------------------------------------------
# Without bleak installed – graceful degradation
# ---------------------------------------------------------------------------


def test_connect_without_bleak_logs_warning(adapter: BluetoothAdapter, caplog) -> None:
    adapter._connected = True  # pre-set, should be cleared
    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", False):
        import asyncio

        asyncio.run(adapter.connect())
    assert not adapter._connected
    assert "bleak is not installed" in caplog.text.lower()


def test_read_temperature_without_bleak_returns_none(
    adapter: BluetoothAdapter, caplog
) -> None:
    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", False):
        import asyncio

        result = asyncio.run(adapter.read_temperature())
    assert result is None
    assert "bleak is not installed" in caplog.text.lower()


def test_bleak_unavailable_connected_stays_false(
    adapter: BluetoothAdapter,
) -> None:
    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", False):
        import asyncio

        async def _run() -> bool:
            await adapter.connect()
            return await adapter.is_connected()

        connected = asyncio.run(_run())
    assert connected is False


def test_disconnect_sets_not_connected(adapter: BluetoothAdapter) -> None:
    adapter._connected = True
    import asyncio

    async def _run() -> bool:
        await adapter.disconnect()
        return await adapter.is_connected()

    connected = asyncio.run(_run())
    assert connected is False


def test_read_temperature_returns_none_when_disconnected(
    adapter: BluetoothAdapter,
) -> None:
    adapter._connected = False
    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", True):
        import asyncio

        result = asyncio.run(adapter.read_temperature())
    assert result is None


# ---------------------------------------------------------------------------
# With bleak mocked – happy path
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.is_connected = True
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    client.read_gatt_char = AsyncMock()
    return client


def test_connect_success_when_bleak_available(mock_client: MagicMock) -> None:
    mock_bleak = MagicMock()
    mock_bleak.BleakClient = MagicMock(return_value=mock_client)
    mock_bleak.BleakError = Exception

    with patch.dict(
        "sys.modules",
        {"bleak": mock_bleak, "bleak.exc": mock_bleak},
    ):
        import importlib

        import device_adapters.adapters.bluetooth as bt_mod

        importlib.reload(bt_mod)

        adapter = bt_mod.BluetoothAdapter("00:11:22:33:44:55")
        import asyncio

        async def _run() -> bool:
            await adapter.connect()
            return await adapter.is_connected()

        connected = asyncio.run(_run())
        assert connected is True
        mock_bleak.BleakClient.assert_called_once_with(
            "00:11:22:33:44:55", timeout=10.0
        )
        mock_client.connect.assert_awaited_once()


def test_read_temperature_returns_parsed_float(mock_client: MagicMock) -> None:
    mantissa = 3660
    exponent = -2
    float_bytes = b"".join(
        [
            mantissa.to_bytes(3, byteorder="little", signed=True),
            exponent.to_bytes(1, byteorder="little", signed=True),
        ]
    )
    raw_response = bytes([0x00]) + float_bytes
    mock_client.read_gatt_char = AsyncMock(return_value=raw_response)

    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", True):
        adapter = BluetoothAdapter("00:11:22:33:44:55")
        adapter._client = mock_client
        adapter._connected = True

        import asyncio

        result = asyncio.run(adapter.read_temperature())
    assert round(result, 1) == 36.6
    mock_client.read_gatt_char.assert_awaited_once_with(
        "00002a1c-0000-1000-8000-00805f34fb"
    )


def test_reconnect_on_read_failure(mock_client: MagicMock) -> None:
    mock_client.read_gatt_char = AsyncMock(side_effect=Exception("BLE timeout"))
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.is_connected = True

    mock_bleak = MagicMock()
    mock_bleak.BleakClient = MagicMock(return_value=mock_client)
    mock_bleak.BleakError = Exception

    with patch.dict(
        "sys.modules",
        {"bleak": mock_bleak, "bleak.exc": mock_bleak},
    ):
        import importlib

        import device_adapters.adapters.bluetooth as bt_mod

        importlib.reload(bt_mod)

        adapter = bt_mod.BluetoothAdapter("00:11:22:33:44:55")
        adapter._client = mock_client
        adapter._connected = True

        import asyncio

        result = asyncio.run(adapter.read_temperature())
        assert result is None
        mock_client.disconnect.assert_awaited_once()
        mock_client.connect.assert_awaited_once()


def test_is_connected_without_bleak(adapter: BluetoothAdapter) -> None:
    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", False):
        import asyncio

        result = asyncio.run(adapter.is_connected())
    assert result is False


def test_is_connected_with_client_attribute() -> None:
    mock_client = MagicMock()
    mock_client.is_connected = True

    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", True):
        adapter = BluetoothAdapter("00:11:22:33:44:55")
        adapter._client = mock_client
        import asyncio

        result = asyncio.run(adapter.is_connected())
    assert result is True


def test_is_connected_client_error_returns_false() -> None:
    class BrokenClient:
        @property
        def is_connected(self) -> bool:
            raise RuntimeError("boom")

    adapter = BluetoothAdapter("00:11:22:33:44:55")
    adapter._client = BrokenClient()

    with patch("device_adapters.adapters.bluetooth.BLEAK_AVAILABLE", True):
        import asyncio

        result = asyncio.run(adapter.is_connected())
    assert result is False
