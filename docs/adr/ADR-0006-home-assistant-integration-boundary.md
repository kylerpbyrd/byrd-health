# ADR-0006: Home Assistant Integration Boundary

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Integration with Home Assistant ecosystem      |

---

## 1. Context

Byrd Health's initial deployment target is a Home Assistant Add-on. The legacy application integrates deeply with HA (Supervisor API, entity publishing, sensor polling, Lovelace card, Ingress). This integration logic must exist but must NOT contaminate the core platform.

Requirements:
- HA integration must work for Phase 2-3 deployment
- Core platform (fertility engine, data service, web API, frontend) must have zero HA dependencies
- Future ByrdOS deployment must be possible by removing/replacing only the HA Bridge
- HA automation scripts (calling API endpoints) must remain compatible

## 2. Decision

All Home Assistant integration logic is confined to a single service: the **HA Bridge**. This service is the ONLY component allowed to import HA-specific libraries or call HA APIs.

### 2.1 HA Bridge Responsibilities

| Responsibility          | Implementation                              | Phase |
|-------------------------|---------------------------------------------|-------|
| Entity publishing       | POST to HA REST API `/states/{entity_id}`   | 2     |
| Entity state polling    | GET from HA REST API `/states/{entity_id}`  | 2     |
| Ingress path handling   | Read `X-Ingress-Path` header; set prefix    | 2     |
| WebSocket relay         | Bridge HA state changes to internal WS      | 3     |
| Lovelace card registration | POST to HA REST API `/lovelace/resources`| 3     |
| bashio config reading   | Read add-on options from HA Supervisor      | 2     |
| Add-on lifecycle         | Startup/shutdown hooks via run.sh           | 2     |

### 2.2 Isolation Contract

```python
# The HA Bridge exposes a clean interface to the platform:

class HABridgeProtocol(Protocol):
    """Interface that the HA Bridge implements. No HA types leak."""

    async def publish_insights(
        self, profile_slug: str, insights: CycleInsights,
        next_period: date | None
    ) -> None: ...

    async def poll_sensor(self, entity_id: str) -> float | None: ...

    async def start_polling(
        self, interval_minutes: int, callback: Callable[[], Any]
    ) -> None: ...

    async def register_lovelace(self, card_url: str) -> None: ...
```

### 2.3 Boundary Enforcement

Enforced by:

1. **Mypy strict mode** — importing `httpx` (used for HA calls) outside `ha_bridge/` triggers a type error (configured via module allowlists)
2. **Import linting** — CI checks that `SUPERVISOR_TOKEN`, `bashio`, `hassio` are only referenced in `ha_bridge/`
3. **Package structure** — `ha_bridge/` is a separate Python package; core packages do not list it as a dependency
4. **Protocol-based dependency** — Core code depends on `HABridgeProtocol`, not the concrete HA implementation

### 2.4 Entity Design (preserved from legacy)

Same 9 entities per profile (`bbt_{slug}_{metric}`). These are proven in production and HA users have automations built on them.

```
sensor.bbt_{slug}_cycle_day
sensor.bbt_{slug}_cycle_phase
sensor.bbt_{slug}_last_temp
binary_sensor.bbt_{slug}_fertile_window
binary_sensor.bbt_{slug}_ovulation_confirmed
sensor.bbt_{slug}_ovulation_date
sensor.bbt_{slug}_next_period_date
sensor.bbt_{slug}_luteal_length
sensor.bbt_{slug}_avg_cycle_length
```

### 2.5 Configuration Flow

```
HA Supervisor bashio config
        │
        ▼
    run.sh reads:
      temp_unit, ha_sensor_entity, poll_interval_minutes
        │
        ▼
    Environment variables:
      BBT_TEMP_UNIT, BBT_HA_SENSOR_ENTITY, BBT_POLL_INTERVAL
        │
        ▼
    HA Bridge reads env vars → translates to internal config model
        │
        ▼
    Platform receives config as Pydantic model (no bashio knowledge)
```

## 3. Consequences

### Positive
- Core platform is fully deployable without HA (standalone for development/testing)
- ByrdOS integration requires only a new bridge implementation
- Testing HA-specific code is isolated from core platform tests
- Clear ownership: Home Assistant Engineer owns HA Bridge; no other agent touches it

### Negative
- Additional abstraction layer (Protocol) between core and HA
- Entity publishing requires the full async pipeline (analysis → insights → bridge call)
- Two deployments to maintain (standalone dev vs. HA add-on)

### Risks
- Protocol may not capture all HA-specific needs — mitigated by starting with the legacy feature set as the baseline
- Entity ID changes would break user automations — mitigated by preserving the legacy naming convention
- Ingress path handling differs between HA versions — mitigated by testing on target HA version

## 4. Phase Timeline

| Phase | HA Integration Scope                                          |
|-------|---------------------------------------------------------------|
| 1     | None — pure platform, no HA code                              |
| 2     | HA Bridge: entity publishing, sensor polling, Ingress support |
| 3     | Lovelace card, WebSocket relay, automation blueprints         |

## 5. References

- `docs/LEGACY_REVIEW.md §4.3` — Legacy HA integration features
- `docs/ARCHITECTURE_RECOMMENDATIONS.md §6` — HA integration recommendations
- `ADR-0001` — Platform architecture (service boundaries)
