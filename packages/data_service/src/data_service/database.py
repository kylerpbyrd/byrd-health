import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event

from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./byrd_health.db")

_engine = create_async_engine(DATABASE_URL, echo=False)

_async_sessionmaker = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


event.listens_for(_engine.sync_engine, "connect")(_set_sqlite_pragma)


async def create_all() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()
