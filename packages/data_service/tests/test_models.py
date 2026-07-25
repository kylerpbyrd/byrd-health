from datetime import date, time
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.models import (
    Profile,
    Cycle,
    Temperature,
    FertilitySigns,
    Symptom,
    ComputedInsights,
)


class TestProfileModel:
    async def test_create_profile(self, async_session: AsyncSession):
        profile = Profile(name="Test", slug="test", temp_unit="F")
        async_session.add(profile)
        await async_session.flush()

        assert profile.id is not None
        assert isinstance(profile.id, UUID)
        assert profile.name == "Test"
        assert profile.slug == "test"
        assert profile.temp_unit == "F"
        assert profile.interpretation_method == "standard"
        assert profile.is_active == False

    async def test_profile_unique_name(self, async_session: AsyncSession):
        profile1 = Profile(name="Unique", slug="unique")
        profile2 = Profile(name="Unique", slug="unique2")
        async_session.add(profile1)
        await async_session.flush()
        async_session.add(profile2)
        with pytest.raises(Exception):
            await async_session.flush()

    async def test_profile_unique_slug(self, async_session: AsyncSession):
        profile1 = Profile(name="One", slug="slug")
        profile2 = Profile(name="Two", slug="slug")
        async_session.add(profile1)
        await async_session.flush()
        async_session.add(profile2)
        with pytest.raises(Exception):
            await async_session.flush()


class TestCycleModel:
    async def test_create_cycle(self, async_session: AsyncSession):
        profile = Profile(name="CycleTest", slug="cycletest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(
            profile_id=profile.id,
            start_date=date(2026, 1, 1),
        )
        async_session.add(cycle)
        await async_session.flush()

        assert cycle.id is not None
        assert cycle.profile_id == profile.id
        assert cycle.start_date == date(2026, 1, 1)
        assert cycle.end_date is None
        assert cycle.cycle_length is None
        assert cycle.notes == ""

    async def test_cycle_relationship(self, async_session: AsyncSession):
        from sqlalchemy.orm import selectinload

        profile = Profile(name="RelTest", slug="reltest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 2, 1))
        async_session.add(cycle)
        await async_session.flush()

        result = await async_session.execute(
            select(Profile)
            .options(selectinload(Profile.cycles))
            .where(Profile.id == profile.id)
        )
        loaded = result.unique().scalar_one()
        assert len(loaded.cycles) == 1
        assert loaded.cycles[0].start_date == date(2026, 2, 1)


class TestTemperatureModel:
    async def test_create_temperature(self, async_session: AsyncSession):
        profile = Profile(name="TempTest", slug="temptest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 3, 1))
        async_session.add(cycle)
        await async_session.flush()

        temp = Temperature(
            cycle_id=cycle.id,
            date=date(2026, 3, 5),
            temp_value=97.8,
            time_taken=time(6, 30),
        )
        async_session.add(temp)
        await async_session.flush()

        assert temp.id is not None
        assert temp.temp_value == 97.8
        assert temp.time_taken == time(6, 30)
        assert temp.is_discarded == False

    async def test_temperature_unique_constraint(self, async_session: AsyncSession):
        profile = Profile(name="UniqTemp", slug="uniqtemp")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 4, 1))
        async_session.add(cycle)
        await async_session.flush()

        t1 = Temperature(cycle_id=cycle.id, date=date(2026, 4, 5), temp_value=97.5)
        t2 = Temperature(cycle_id=cycle.id, date=date(2026, 4, 5), temp_value=97.8)
        async_session.add(t1)
        await async_session.flush()
        async_session.add(t2)
        with pytest.raises(Exception):
            await async_session.flush()


class TestFertilitySignsModel:
    async def test_create_fertility_signs(self, async_session: AsyncSession):
        profile = Profile(name="SignsTest", slug="signstest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 5, 1))
        async_session.add(cycle)
        await async_session.flush()

        signs = FertilitySigns(
            cycle_id=cycle.id,
            date=date(2026, 5, 3),
            menstrual_flow="medium",
            cervical_mucus="eggwhite",
        )
        async_session.add(signs)
        await async_session.flush()

        assert signs.menstrual_flow == "medium"
        assert signs.cervical_mucus == "eggwhite"
        assert signs.cervical_position is None


class TestSymptomModel:
    async def test_create_symptom(self, async_session: AsyncSession):
        profile = Profile(name="SympTest", slug="symptest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 6, 1))
        async_session.add(cycle)
        await async_session.flush()

        symptom = Symptom(
            cycle_id=cycle.id,
            date=date(2026, 6, 2),
            symptom_type="headache",
            severity=2,
        )
        async_session.add(symptom)
        await async_session.flush()

        assert symptom.symptom_type == "headache"
        assert symptom.severity == 2


class TestComputedInsightsModel:
    async def test_create_insights(self, async_session: AsyncSession):
        profile = Profile(name="InsightTest", slug="insighttest")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 7, 1))
        async_session.add(cycle)
        await async_session.flush()

        insights = ComputedInsights(
            cycle_id=cycle.id,
            coverline=97.8,
            ovulation_date=date(2026, 7, 15),
            ovulation_confirmed=True,
            ovulation_method="standard",
            engine_version="1.0.0",
        )
        async_session.add(insights)
        await async_session.flush()

        assert insights.coverline == 97.8
        assert insights.ovulation_confirmed == True
        assert insights.pregnancy_indicator == False
        assert insights.engine_version == "1.0.0"

    async def test_insights_unique_per_cycle(self, async_session: AsyncSession):
        profile = Profile(name="UniqIns", slug="uniqins")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 8, 1))
        async_session.add(cycle)
        await async_session.flush()

        ins1 = ComputedInsights(cycle_id=cycle.id)
        ins2 = ComputedInsights(cycle_id=cycle.id)
        async_session.add(ins1)
        await async_session.flush()
        async_session.add(ins2)
        with pytest.raises(Exception):
            await async_session.flush()


class TestCascadeDeletes:
    async def test_delete_profile_cascades(self, async_session: AsyncSession):
        profile = Profile(name="Cascade", slug="cascade")
        async_session.add(profile)
        await async_session.flush()

        cycle = Cycle(profile_id=profile.id, start_date=date(2026, 9, 1))
        async_session.add(cycle)
        await async_session.flush()

        temp = Temperature(cycle_id=cycle.id, date=date(2026, 9, 2), temp_value=97.5)
        async_session.add(temp)
        await async_session.flush()

        await async_session.delete(profile)
        await async_session.flush()

        result = await async_session.execute(
            select(Cycle).where(Cycle.id == cycle.id)
        )
        assert result.scalar_one_or_none() is None

        result = await async_session.execute(
            select(Temperature).where(Temperature.id == temp.id)
        )
        assert result.scalar_one_or_none() is None
