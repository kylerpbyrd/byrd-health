from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data_service.models import Base, Profile
from data_service.service import DataService

from .config import settings

_engine = create_async_engine(settings.database_url, echo=settings.debug)

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
    return DataService(session)


async def get_active_profile(
    data_svc: DataService = Depends(get_data_service),
) -> Profile:
    profile = await data_svc.get_active_profile()
    if profile is None:
        raise HTTPException(status_code=404, detail="No active profile found")
    return profile
