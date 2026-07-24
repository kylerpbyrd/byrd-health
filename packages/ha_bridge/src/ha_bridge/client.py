import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_HA_API_BASE = "http://supervisor/core/api"
_DEFAULT_TIMEOUT = 5.0


class HAClient:
    """Async HTTP client for Home Assistant Supervisor REST API."""

    def __init__(self, base_url: str = _HA_API_BASE, token: str | None = None) -> None:
        self._base_url = base_url
        self._token = token if token is not None else os.environ.get("SUPERVISOR_TOKEN", "")
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(_DEFAULT_TIMEOUT))

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[Any] | None:
        if not self._token:
            return None

        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        try:
            response = await self._client.request(method, url, json=payload, headers=headers)
            if response.status_code == 401:
                logger.error("HA API: Unauthorized — check SUPERVISOR_TOKEN")
                return None
            if response.status_code == 404:
                logger.debug("HA API %s %s → 404 not found", method, path)
                return None
            if response.status_code >= 400:
                logger.warning("HA API %s %s → HTTP %d", method, path, response.status_code)
                return None
            return response.json()  # type: ignore[no-any-return]
        except httpx.TimeoutException:
            logger.warning("HA API %s %s timed out", method, path)
            return None
        except Exception as exc:
            logger.debug("HA API %s %s failed: %s", method, path, exc)
            return None

    async def post_state(self, entity_id: str, state: str, attributes: dict[str, Any] | None = None) -> bool:
        payload: dict[str, Any] = {"state": state}
        if attributes:
            payload["attributes"] = {k: v for k, v in attributes.items() if v is not None}
        result = await self._request("POST", f"/states/{entity_id}", payload)
        return result is not None

    async def get_state(self, entity_id: str) -> dict[str, Any] | None:
        result = await self._request("GET", f"/states/{entity_id}")
        if isinstance(result, dict):
            return result
        return None

    async def get_lovelace_resources(self) -> list[dict[str, Any]] | None:
        result = await self._request("GET", "/lovelace/resources")
        if isinstance(result, list):
            return result
        return None

    async def create_lovelace_resource(self, url: str, res_type: str = "module") -> bool:
        result = await self._request("POST", "/lovelace/resources", {"res_type": res_type, "url": url})
        return result is not None

    async def delete_lovelace_resource(self, resource_id: str) -> bool:
        result = await self._request("DELETE", f"/lovelace/resources/{resource_id}")
        return result is not None
