# BLE Basal Body Thermometer Research

## Common BBT Thermometer Brands

| Brand | Type | Connectivity | Notes |
|-------|------|-------------|-------|
| Easy@Home | Smart BBT | BLE | One of the most popular BBTs. Likely uses standard HTP or custom service. App-based pairing. |
| Femometer | Smart BBT (Vinca/Vinca II) | BLE | Popular on Amazon. Uses **custom GATT services** (not standard HTP). Requires app for history. |
| Tempdrop | Wearable armband | BLE | Worn overnight. Uses proprietary algorithms. Likely custom BLE service. |
| iFertracker | Wearable (Raiing) | BLE | Worn under arm overnight. Custom BLE services. |
| OvuSense | Vaginal sensor | BLE | Medical-grade. Custom app integration. |
| Daysy/Mira | Standalone + app | BLE | Primarily standalone with Bluetooth sync. |
| ThermoBeacon | General BLE thermometer | BLE | HA-integrated via `thermobeacon` integration. Uses BLE advertisements, no connection needed. |
| Oral-B iO | Electric toothbrush (reference) | BLE | Already HA-integrated. Shows pattern for BLE peripheral handling. |

## GATT Service UUIDs

### Standard Health Thermometer Service (HTS)

- **Service UUID**: `0x1809` (00001809-0000-1000-8000-00805F9B34FB)
- **Temperature Measurement Characteristic**: `0x2A1C`
- **Temperature Measurement**: Uses `INDICATE` (not `NOTIFY`) — requires client acknowledgment
- **Temperature Type Characteristic**: `0x2A1D`
- **Measurement Interval Characteristic**: `0x2A21`
- **Data Format**: IEEE 11073-20601 FLOAT (32-bit, little-endian, in Celsius)

Most medical-grade temperature sensors implement this standard profile. The temperature value is encoded as a 32-bit IEEE 11073 FLOAT:
- First byte: exponent (signed int8)
- Bytes 2-4: mantissa (int24, little-endian)
- Actual value = mantissa * 10^exponent

### IEEE 11073-20601 Float Parsing

```python
import struct

def parse_ieee11073_float(data: bytes) -> float:
    """Parse a 4-byte IEEE 11073-20601 FLOAT to Python float."""
    mantissa = int.from_bytes(data[0:3], byteorder="little", signed=True)
    exponent = data[3] if data[3] < 128 else data[3] - 256  # signed int8
    return mantissa * (10.0 ** exponent)
```

For standard HTP, the Temperature Measurement characteristic returns 5 bytes. The first byte is a flags field, and bytes 1-4 are the IEEE 11073 float.

### Common Custom UUIDs (Brand-Specific)

Exact custom UUIDs for Femometer, Tempdrop, etc. cannot be confirmed without hardware or reverse-engineering. These products typically use:
- A custom primary service UUID
- A temperature data characteristic within that service
- Often paired with battery level and timestamp characteristics

### ThermoBeacon Reference (HA Integration)

The Home Assistant `thermobeacon` integration listens for BLE **advertisements** (no active connection). The temperature data is embedded directly in the manufacturer data portion of advertising packets. This avoids GATT connections entirely.

## Connection Patterns

### Advertising
- BBT thermometers typically broadcast BLE advertisements when turned on or after measurement
- Many thermometers only advertise for 30-120 seconds after a reading is taken
- Advertising interval typically 100ms-1s

### Pairing/Bonding
- Most consumer BBT thermometers do NOT require traditional Bluetooth pairing/bonding
- They use BLE GATT connection without bonding (Just Works pairing)
- Data is read via GATT characteristic reads, not notifications in many cases
- Some use `INDICATE` (acknowledged notifications) from the Health Thermometer Service

### Connection Flow
1. Scan for device advertising the Health Thermometer Service (0x1809) or known name prefix
2. Connect via `BleakClient`
3. Discover services
4. Read Temperature Measurement characteristic (0x2A1C)
5. Parse IEEE 11073 float
6. Disconnect

## Home Assistant Bluetooth Integration Notes

### BlueZ Stack
- HA uses BlueZ >= 5.43 (5.63+ recommended) on Linux
- D-Bus is the interface between HA and BlueZ
- BLE requires `NET_ADMIN` and `NET_RAW` capabilities in Docker
- The `dbus-broker` is the recommended D-Bus implementation

### BLE Adapter Requirements
- HA OS 9.0+ includes all Bluetooth patches
- HA Container must mount `/run/dbus:/run/dbus:ro`
- Passive scanning available with BlueZ 5.63+

### Permissions
- The `bluetooth` integration in HA handles adapter management
- Our BLE adapter must not interfere with HA's own BLE stack
- For an add-on, the add-on must request Bluetooth permissions via `host_dbus` access
- BLE adapters require: `bluetooth:`, `host_dbus: true`, `apparmor: false`

### Byrds Health Add-on Considerations
- The add-on accesses the host's BlueZ via D-Bus
- Our `BluetoothAdapter` uses `bleak` which in turn uses BlueZ via D-Bus on Linux
- On non-Linux platforms (Windows/macOS), bleak uses the native BLE stack
- For testing without hardware, we mock bleak entirely

## Design Decision: Default to Standard HTP

Since specific UUIDs for most BBT brands cannot be confirmed without hardware:
- **Default**: Use standard Health Thermometer Service (0x1809) and Temperature Measurement (0x2A1C)
- **Extensible**: Accept optional custom service/characteristic UUIDs in constructor
- **Future**: Add brand-specific adapters that subclass BluetoothAdapter with known UUIDs
