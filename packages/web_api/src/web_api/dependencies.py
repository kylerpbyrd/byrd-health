import os
from collections.abc import AsyncGenerator
from typing import Any

from data_service.models import Profile
from data_service.service import DataService
from fastapi import Depends, HTTPException
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings
from .ha_protocol import HABridgeProtocol
from .websocket import WebSocketBroker

_engine = create_async_engine(settings.database_url, echo=settings.debug)

_ha_bridge: HABridgeProtocol | None = None
_ws_broker: WebSocketBroker | None = None
_device_registry = None  # DeviceRegistry | None (lazy import to avoid circular deps)


def get_ha_bridge(requested: bool = False) -> HABridgeProtocol | None:
    if requested and _ha_bridge is None:
        import logging
        logging.getLogger(__name__).warning("HA Bridge requested but not initialized")
    return _ha_bridge


def set_ha_bridge(bridge: HABridgeProtocol | None) -> None:
    global _ha_bridge
    _ha_bridge = bridge


def get_ws_broker() -> WebSocketBroker | None:
    return _ws_broker


def set_ws_broker(broker: WebSocketBroker | None) -> None:
    global _ws_broker
    _ws_broker = broker


def get_device_registry():
    return _device_registry


def set_device_registry(registry) -> None:
    global _device_registry
    _device_registry = registry

_async_sessionmaker = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


event.listens_for(_engine.sync_engine, "connect")(_set_sqlite_pragma)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _async_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_data_service(session: AsyncSession = Depends(get_db)) -> DataService:
    secret_key = os.environ.get("BYRD_SECRET_KEY")
    return DataService(session, secret_key=secret_key)


async def get_active_profile(
    data_svc: DataService = Depends(get_data_service),
) -> Profile:
    profile = await data_svc.get_active_profile()
    if profile is None:
        raise HTTPException(status_code=404, detail="No active profile found")
    return profile
