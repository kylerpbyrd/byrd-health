import pytest
from ha_bridge.client import HAClient


class MockHAClient(HAClient):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._get_state_return: dict | None = None

    async def _request(self, method: str, path: str, payload: dict | None = None) -> object:
        return self._get_state_return

    async def get_state(self, entity_id: str) -> dict | None:
        return self._get_state_return


@pytest.fixture
def mock_client() -> MockHAClient:
    return MockHAClient()
