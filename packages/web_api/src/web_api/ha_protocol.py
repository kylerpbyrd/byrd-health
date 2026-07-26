from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HABridgeProtocol(Protocol):
    async def publish_entities(self, profile_slug: str) -> None: ...
    async def publish_all_profiles(self) -> None: ...
    async def startup(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def publish_insights(
        self,
        slug: str,
        name: str,
        temp_unit: str,
        insights: dict[str, Any],
        next_period: str | None = None,
    ) -> None: ...
