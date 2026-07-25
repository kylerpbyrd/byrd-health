import os
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data_service.models import Base, Profile
from data_service.service import DataService

from .config import settings

from ha_bridge.bridge import HABridge

_engine = create_async_engine(settings.database_url, echo=settings.debug)

_ha_bridge: HABridge | None = None


def get_ha_bridge(requested: bool = False) -> HABridge | None:
    if requested and _ha_bridge is None:
        import logging
        logging.getLogger(__name__).warning("HA Bridge requested but not initialized")
    return _ha_bridge


def set_ha_bridge(bridge: HABridge | None) -> None:
    global _ha_bridge
    _ha_bridge = bridge

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
