import pytest

from ha_bridge.client import HAClient


class MockHAClient(HAClient):
    """Test double that records entity POSTs instead of calling real HA."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.posted_states: list[dict] = []
        self._return_value: object = {"success": True}
        self._get_state_return: dict | None = None
        self._lovelace_resources: list[dict] | None = []
        self._should_fail: bool = False
        self._delete_calls: list[str] = []
        self._create_resource_calls: list[dict] = []
        self.service_calls: list[dict] = []
        self._ingress_url: str | None = None
        self._supervisor_info: dict | None = None

    async def _request(self, method: str, path: str, payload: dict | None = None) -> object:
        if self._should_fail:
            return None
        return self._return_value

    async def post_state(self, entity_id: str, state: str, attributes: dict | None = None) -> bool:
        cleaned = {k: v for k, v in (attributes or {}).items() if v is not None}
        self.posted_states.append({"entity_id": entity_id, "state": state, "attributes": cleaned})
        return True

    async def get_state(self, entity_id: str) -> dict | None:
        return self._get_state_return

    async def get_lovelace_resources(self) -> list[dict] | None:
        return self._lovelace_resources

    async def create_lovelace_resource(self, url: str, res_type: str = "module") -> bool:
        self._create_resource_calls.append({"url": url, "res_type": res_type})
        return True

    async def delete_lovelace_resource(self, resource_id: str) -> bool:
        self._delete_calls.append(resource_id)
        return True

    async def call_service(self, domain: str, service: str, data: dict | None = None) -> bool:
        self.service_calls.append({"domain": domain, "service": service, "data": data})
        return True

    async def get_supervisor_addon_info(self) -> dict | None:
        return self._supervisor_info

    async def get_ingress_url(self) -> str | None:
        if self._ingress_url is not None:
            return self._ingress_url
        info = self._supervisor_info
        if info and isinstance(info, dict):
            return info.get("ingress_url") or None
        return None


@pytest.fixture
def mock_client() -> MockHAClient:
    return MockHAClient()


@pytest.fixture
def sample_insights() -> dict:
    return {
        "cycle_day": 14,
        "phase": "luteal",
        "last_temp": 97.832,
        "ovulation_confirmed": True,
        "ovulation_date": "2026-01-14",
        "fertile_start_date": "2026-01-08",
        "fertile_end_date": "2026-01-16",
        "luteal_length": 14,
        "avg_cycle_length": 28,
    }


@pytest.fixture
def minimal_insights() -> dict:
    return {
        "cycle_day": 1,
        "phase": "follicular",
    }
