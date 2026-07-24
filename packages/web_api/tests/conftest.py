import asyncio
from datetime import date, time
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data_service.models import Base
from data_service.service import DataService


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with sessionmaker() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(async_engine):
    from web_api.app import create_app

    sessionmaker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with sessionmaker() as session:
            try:
                yield session
            finally:
                await session.close()

    from web_api.dependencies import get_db

    app = create_app(lifespan=None)
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_profile(async_session):
    from data_service.repositories import ProfileRepository

    repo = ProfileRepository(async_session)
    profile = await repo.create("Test Profile", "F")
    profile.is_active = True
    await async_session.commit()
    return profile


@pytest_asyncio.fixture
async def test_cycle(async_session, test_profile):
    from data_service.repositories import CycleRepository

    repo = CycleRepository(async_session)
    cycle = await repo.create(test_profile.id, date.today())
    await async_session.commit()
    return cycle


@pytest_asyncio.fixture
async def seeded_entry(async_session, test_cycle):
    from data_service.repositories import EntryRepository

    repo = EntryRepository(async_session)
    temp = await repo.upsert_temperature(
        cycle_id=test_cycle.id,
        entry_date=date.today(),
        temp_value=97.5,
        time_taken=time(6, 30),
    )
    signs = await repo.upsert_signs(
        cycle_id=test_cycle.id,
        entry_date=date.today(),
        cervical_mucus="watery",
    )
    await async_session.commit()
    return {"temperature": temp, "signs": signs}
