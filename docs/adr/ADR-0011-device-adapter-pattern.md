# ADR-0011: Device Adapter Pattern

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Proposed                                       |
| **Date**     | 2026-07-26                                     |
| **Deciders** | Lead Architect                                 |
| **Replaces** | None                                           |
| **Scope**    | Device integration architecture                |

---

## 1. Context

Byrd Health currently supports manual temperature entry and optional HA sensor polling. Phase 3 introduces automatic data ingestion from external devices:

- Bluetooth basal body thermometers (e.g., Easy@Home, Femometer, Tempdrop)
- ESPHome-connected sensors (temperature, pulse, sleep)
- Wearable APIs (Apple Health, Google Health Connect, Oura, Fitbit)
- HA entities published by other integrations

Each device type has its own protocol, data format, connection lifecycle, and reliability characteristics. We need an architecture that adds device support without modifying the core platform.

Requirements:
- Core platform must remain device-agnostic
- Adding a new device type must not require changes to fertility_engine or data_service
- Device adapters must be independently testable with simulated data
- Must support eventual ByrdOS deployment (devices connect directly, not through HA)

## 2. Decision

Use an **Adapter Pattern** with a standardized protocol. Each device type gets its own adapter package that implements a common interface.

### 2.1 Adapter Protocol

```python
from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class DeviceAdapter(Protocol):
    """Protocol that all device adapters must implement."""

    @property
    def device_id(self) -> str: ...

    @property
    def device_type(self) -> str: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    async def read_temperature(self) -> float | None: ...

    async def is_connected(self) -> bool: ...
```

### 2.2 Adapter Registry

A central `DeviceRegistry` manages all active adapters:

```python
class DeviceRegistry:
    def register(self, adapter: DeviceAdapter) -> None: ...
    def unregister(self, device_id: str) -> None: ...
    async def read_all(self) -> dict[str, float]: ...
```

This exposes a `GET /api/v1/fertility/devices` endpoint and enables auto-population of the entry form with the latest readings.

### 2.3 Package Structure

```
packages/
├── device_adapters/              # New top-level package (Phase 3)
│   ├── pyproject.toml
│   ├── src/device_adapters/
│   │   ├── __init__.py
│   │   ├── protocol.py           # DeviceAdapter protocol
│   │   ├── registry.py           # DeviceRegistry
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── esphome.py        # ESPHome adapter (HA API)
│   │       ├── bluetooth.py      # BLE thermometer adapter
│   │       ├── ha_sensor.py      # Generic HA entity adapter (existing)
│   │       └── wearable.py       # Wearable API adapter
│   └── tests/
│       ├── test_registry.py
│       ├── test_esphome.py
│       └── test_bluetooth.py
```

### 2.4 Web API Integration

The web_api adds device endpoints:

```
GET  /api/v1/fertility/devices              # List registered devices
POST /api/v1/fertility/devices/{id}/read    # Trigger a reading
GET  /api/v1/fertility/devices/{id}/status  # Connection status
```

The entry form pre-fills temperature from the selected device.

### 2.5 Configuration

Devices are configured as a new top-level option in `config.yaml`:

```yaml
devices:
  - type: ha_sensor
    entity_id: sensor.bbt_thermometer
    name: "Bedroom Thermometer"
  - type: esphome
    name: "BBT Sensor"
    host: 192.168.1.100
  - type: bluetooth
    name: "Tempdrop"
    address: "00:11:22:33:44:55"
```

## 3. Consequences

### Positive
- Core platform stays device-agnostic (no new dependencies in fertility_engine or data_service)
- New devices can be added in hours, not days
- Adapters are independently testable with simulated data
- Same pattern works for HA add-on and future ByrdOS

### Negative
- Additional package with its own dependency surface
- Bluetooth adapters require OS-level BLE stack (bluez on Linux)
- Wearable APIs require OAuth credentials management
- Device configuration adds complexity to the add-on options UI

### Risks
- Bluetooth permissions differ across HA Supervisor versions — mitigated by testing on target HA version
- BLE adapters consume significant power on battery-powered HA devices — mitigated by configurable polling intervals
- Wearable API rate limits may delay readings — mitigated by caching and fallback to manual entry

## 4. Phase Timing

| Phase | Device Scope |
|-------|-------------|
| 3.1   | HA Sensor Adapter (lift existing polling into adapter pattern) |
| 3.2   | ESPHome Adapter (native API, no cloud) |
| 3.3   | Bluetooth Thermometer Adapter (BLE GATT) |
| 3.4   | Wearable APIs (Oura, Apple Health, Google Health Connect) |

## 5. References

- `ADR-0006` — HA Bridge isolation pattern (applied to device adapters)
- `ADR-0001` — Service boundary principles
- `docs/research/bt-thermometers.md` — Planned research document
