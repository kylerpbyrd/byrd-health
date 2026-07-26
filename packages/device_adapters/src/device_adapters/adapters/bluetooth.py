from __future__ import annotations

import asyncio
import logging
import struct
from typing import Any

logger = logging.getLogger(__name__)

try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakError

    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    BleakClient = None  # type: ignore
    BleakScanner = None  # type: ignore
    BleakError = Exception  # type: ignore

HEALTH_THERMOMETER_SERVICE_UUID = "00001809-0000-1000-8000-00805f34fb"
TEMPERATURE_MEASUREMENT_CHAR_UUID = "00002a1c-0000-1000-8000-00805f34fb"


def _parse_ieee11073_float(data: bytes) -> float:
    """Parse a 4-byte IEEE 11073-20601 FLOAT to a Python float."""
    if len(data) < 4:
        raise ValueError(
            f"IEEE 11073 float requires 4 bytes, got {len(data)}"
        )
    mantissa = int.from_bytes(data[0:3], byteorder="little", signed=True)
    exponent = data[3]
    if exponent > 127:
        exponent -= 256
    return float(mantissa) * (10.0 ** exponent)


class BluetoothAdapter:
    """BLE thermometer adapter.

    Uses bleak for BLE communication. Degrades gracefully if bleak is not
    installed.  By default targets the standard Bluetooth Health Thermometer
    Service (0x1809).

    Optional dependency: ``bleak`` (``pip install bleak``)
    """

    def __init__(
        self,
        address: str,
        device_id: str | None = None,
        name: str = "Bluetooth Thermometer",
        service_uuid: str = HEALTH_THERMOMETER_SERVICE_UUID,
        characteristic_uuid: str = TEMPERATURE_MEASUREMENT_CHAR_UUID,
    ) -> None:
        self._address = address
        self._device_id = device_id or f"ble_{address.replace(':', '_')}"
        self._name = name
        self._service_uuid = service_uuid
        self._characteristic_uuid = characteristic_uuid
        self._connected = False
        self._latest_value: float | None = None
        self._client: Any = None

    # ------------------------------------------------------------------
    # DeviceAdapter protocol
    # ------------------------------------------------------------------

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> str:
        return "bluetooth"

    async def connect(self) -> None:
        if not BLEAK_AVAILABLE:
            logger.warning(
                "bleak is not installed – cannot connect to %s (%s). "
                "Install with: pip install bleak",
                self._name,
                self._address,
            )
            self._connected = False
            return

        try:
            self._client = BleakClient(self._address, timeout=10.0)
            await self._client.connect()
            self._connected = True
            logger.info(
                "Connected to %s (%s)", self._name, self._address
            )
        except BleakError as exc:
            logger.error(
                "Failed to connect to %s (%s): %s",
                self._name,
                self._address,
                exc,
            )
            self._connected = False
            self._client = None

    async def disconnect(self) -> None:
        if self._client and self._client.is_connected:
            try:
                await self._client.disconnect()
            except BleakError as exc:
                logger.warning(
                    "Error disconnecting from %s: %s", self._name, exc
                )
        self._client = None
        self._connected = False

    async def read_temperature(self) -> float | None:
        if not BLEAK_AVAILABLE:
            logger.warning(
                "bleak is not installed – cannot read temperature from %s",
                self._name,
            )
            return None

        if not self._connected or self._client is None:
            return None

        try:
            raw = await self._client.read_gatt_char(
                self._characteristic_uuid
            )
            value = self._parse_temperature_response(raw)
            self._latest_value = value
            return value
        except (BleakError, asyncio.TimeoutError) as exc:
            logger.warning(
                "BLE read failed for %s: %s – attempting reconnect",
                self._name,
                exc,
            )
            await self._reconnect()
            return None
        except Exception as exc:
            logger.error(
                "Unexpected error reading temperature from %s: %s",
                self._name,
                exc,
            )
            return None

    async def is_connected(self) -> bool:
        if not BLEAK_AVAILABLE:
            return False
        if self._client is not None:
            try:
                return self._client.is_connected
            except Exception:
                return False
        return self._connected

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _reconnect(self) -> None:
        await self.disconnect()
        self._connected = False
        try:
            await self.connect()
        except Exception as exc:
            logger.error(
                "Reconnect failed for %s: %s", self._name, exc
            )
            self._connected = False

    def _parse_temperature_response(self, raw: bytes) -> float:
        if raw and len(raw) >= 5:
            data = raw[1:5]
        else:
            data = raw

        return _parse_ieee11073_float(data)
