from datetime import date, time

from data_service.repositories import (
    CycleRepository,
    EntryRepository,
    ExportRepository,
    InsightsRepository,
    ProfileRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


class TestProfileRepository:
    async def test_create(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        profile = await repo.create("Alice", "C")
        assert profile.name == "Alice"
        assert profile.slug == "alice"
        assert profile.temp_unit == "C"

    async def test_get_all(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        await repo.create("User1")
        await repo.create("User2")
        all_profiles = await repo.get_all()
        assert len(all_profiles) == 2

    async def test_get_by_id(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        profile = await repo.create("Target")
        await async_session.commit()

        found = await repo.get_by_id(profile.id)
        assert found is not None
        assert found.name == "Target"

    async def test_get_by_id_not_found(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        from uuid import uuid4
        found = await repo.get_by_id(uuid4())
        assert found is None

    async def test_get_active(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        p1 = await repo.create("Inactive")
        p2 = await repo.create("Active")
        p2.is_active = True
        await async_session.commit()

        active = await repo.get_active()
        assert active is not None
        assert active.name == "Active"

    async def test_get_active_fallback_to_first(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        await repo.create("Only")

        active = await repo.get_active()
        assert active is not None
        assert active.name == "Only"

    async def test_set_active(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        p1 = await repo.create("First")
        p1.is_active = True
        p2 = await repo.create("Second")
        await async_session.commit()

        result = await repo.set_active(p2.id)
        assert result is not None
        assert result.id == p2.id

        await async_session.refresh(p1)
        assert p1.is_active == False
        await async_session.refresh(p2)
        assert p2.is_active == True

    async def test_delete(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        profile = await repo.create("DeleteMe")
        await async_session.commit()

        result = await repo.delete(profile.id)
        assert result == True

        found = await repo.get_by_id(profile.id)
        assert found is None

    async def test_update_settings(self, async_session: AsyncSession):
        repo = ProfileRepository(async_session)
        profile = await repo.create("Settings", "F")
        await async_session.commit()

        updated = await repo.update_settings(
            profile.id, temp_unit="C", interpretation_method="fertility_awareness"
        )
        assert updated is not None
        assert updated.temp_unit == "C"
        assert updated.interpretation_method == "fertility_awareness"


class TestCycleRepository:
    async def test_create(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("CycleUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 1, 10))
        assert cycle.profile_id == profile.id
        assert cycle.start_date == date(2026, 1, 10)

    async def test_get_or_create_current_new(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("NewCycle")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.get_or_create_current(profile.id)
        assert cycle.profile_id == profile.id
        assert cycle.end_date is None

    async def test_get_or_create_current_existing(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("Existing")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        first = await cycle_repo.get_or_create_current(profile.id)
        await async_session.commit()
        second = await cycle_repo.get_or_create_current(profile.id)
        assert first.id == second.id

    async def test_close_cycle(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("CloseUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 1, 1))
        await async_session.commit()

        closed = await cycle_repo.close_cycle(cycle.id, date(2026, 1, 30))
        assert closed is not None
        assert closed.end_date == date(2026, 1, 30)
        assert closed.cycle_length == 29

    async def test_close_cycle_profile_ownership(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        p1 = await profile_repo.create("Owner1")
        p2 = await profile_repo.create("Owner2")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(p1.id, date(2026, 1, 1))
        await async_session.commit()

        closed = await cycle_repo.close_cycle(
            cycle.id, date(2026, 1, 30), profile_id=p2.id
        )
        assert closed is None

    async def test_get_past_lengths(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("Lengths")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        c1 = await cycle_repo.create(profile.id, date(2026, 1, 1))
        await cycle_repo.close_cycle(c1.id, date(2026, 1, 28))
        c2 = await cycle_repo.create(profile.id, date(2026, 2, 1))
        await cycle_repo.close_cycle(c2.id, date(2026, 3, 1))
        await async_session.commit()

        lengths = await cycle_repo.get_past_lengths(profile.id)
        assert 27 in lengths
        assert 28 in lengths


class TestEntryRepository:
    async def test_upsert_temperature_insert(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("EntryUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 3, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        temp = await entry_repo.upsert_temperature(
            cycle.id, date(2026, 3, 5), 97.8, time(6, 30)
        )
        assert temp.temp_value == 97.8
        assert temp.time_taken == time(6, 30)

    async def test_upsert_temperature_update(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("UpdateUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 4, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        await entry_repo.upsert_temperature(cycle.id, date(2026, 4, 3), 97.5)
        updated = await entry_repo.upsert_temperature(
            cycle.id, date(2026, 4, 3), 98.2, notes="Updated temp"
        )
        assert updated.temp_value == 98.2
        assert updated.notes == "Updated temp"

    async def test_upsert_signs(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("SignsUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 5, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        signs = await entry_repo.upsert_signs(
            cycle.id,
            date(2026, 5, 3),
            menstrual_flow="heavy",
            cervical_mucus="creamy",
        )
        assert signs.menstrual_flow == "heavy"
        assert signs.cervical_mucus == "creamy"

    async def test_upsert_symptoms_replace(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("SympUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 6, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        items = [
            {"symptom_type": "headache", "severity": 2},
            {"symptom_type": "fatigue", "severity": 3},
        ]
        result = await entry_repo.upsert_symptoms(cycle.id, date(2026, 6, 5), items)
        assert len(result) == 2

        items2 = [{"symptom_type": "nausea", "severity": 1}]
        result2 = await entry_repo.upsert_symptoms(cycle.id, date(2026, 6, 5), items2)
        assert len(result2) == 1
        assert result2[0].symptom_type == "nausea"

        all_symptoms = await entry_repo.get_symptoms_for_cycle(cycle.id)
        assert len(all_symptoms) == 1

    async def test_get_recent_temps(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("RecentUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 7, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        for i in range(20):
            await entry_repo.upsert_temperature(
                cycle.id, date(2026, 7, i + 1), 97.0 + i * 0.1
            )
        await async_session.commit()

        recent = await entry_repo.get_recent_temps(cycle.id, limit=14)
        assert len(recent) == 14

    async def test_get_temps_for_cycle(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("CycleTemps")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 8, 1))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        await entry_repo.upsert_temperature(cycle.id, date(2026, 8, 1), 97.5)
        await entry_repo.upsert_temperature(cycle.id, date(2026, 8, 2), 97.8)
        await async_session.commit()

        temps = await entry_repo.get_temps_for_cycle(cycle.id)
        assert len(temps) == 2


class TestInsightsRepository:
    async def test_upsert_insert(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("InsUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 9, 1))
        await async_session.commit()

        repo = InsightsRepository(async_session)
        insights = await repo.upsert(
            cycle.id,
            {
                "coverline": 97.8,
                "ovulation_confirmed": True,
                "engine_version": "1.0.0",
            },
        )
        assert insights.coverline == 97.8
        assert insights.ovulation_confirmed == True

    async def test_upsert_update(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("InsUpdate")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 10, 1))
        await async_session.commit()

        repo = InsightsRepository(async_session)
        await repo.upsert(
            cycle.id,
            {
                "coverline": 97.5,
                "pregnancy_indicator": False,
            },
        )
        await async_session.commit()

        updated = await repo.upsert(
            cycle.id,
            {
                "coverline": 98.0,
                "pregnancy_indicator": True,
            },
        )
        assert updated.coverline == 98.0
        assert updated.pregnancy_indicator == True

    async def test_get_for_cycle(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("InsGet")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 11, 1))
        await async_session.commit()

        repo = InsightsRepository(async_session)
        await repo.upsert(
            cycle.id,
            {"ovulation_date": date(2026, 11, 15), "luteal_length": 14},
        )
        await async_session.commit()

        found = await repo.get_for_cycle(cycle.id)
        assert found is not None
        assert found.ovulation_date == date(2026, 11, 15)
        assert found.luteal_length == 14


class TestExportRepository:
    async def test_export_profile(self, async_session: AsyncSession):
        profile_repo = ProfileRepository(async_session)
        profile = await profile_repo.create("ExportUser")
        await async_session.commit()

        cycle_repo = CycleRepository(async_session)
        cycle = await cycle_repo.create(profile.id, date(2026, 12, 1))
        await cycle_repo.close_cycle(cycle.id, date(2026, 12, 28))
        await async_session.commit()

        entry_repo = EntryRepository(async_session)
        await entry_repo.upsert_temperature(cycle.id, date(2026, 12, 5), 97.8)
        await entry_repo.upsert_signs(
            cycle.id, date(2026, 12, 5), menstrual_flow="light"
        )
        await async_session.commit()

        export_repo = ExportRepository(async_session)
        data = await export_repo.export_profile(profile.id)

        assert data is not None
        assert data["profile"].name == "ExportUser"
        assert len(data["cycles"]) == 1
        assert len(data["cycles"][0]["temperatures"]) == 1
        assert len(data["cycles"][0]["fertility_signs"]) == 1

    async def test_export_profile_nonexistent(self, async_session: AsyncSession):
        from uuid import uuid4

        export_repo = ExportRepository(async_session)
        data = await export_repo.export_profile(uuid4())
        assert data is None
