from datetime import date, datetime, timezone
from uuid import UUID
from typing import Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Profile, Cycle, Temperature, FertilitySigns, Symptom, ComputedInsights


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, name: str, temp_unit: str = "F") -> Profile:
        import re

        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "_", slug)
        slug = slug.strip("_") or "profile"

        profile = Profile(name=name, slug=slug, temp_unit=temp_unit)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_all(self) -> list[Profile]:
        result = await self.session.execute(
            select(Profile).order_by(Profile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, profile_id: UUID) -> Profile | None:
        result = await self.session.execute(
            select(Profile).where(Profile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_active(self) -> Profile | None:
        result = await self.session.execute(
            select(Profile).where(Profile.is_active == True).order_by(Profile.id).limit(1)
        )
        active = result.scalar_one_or_none()
        if active:
            return active
        result = await self.session.execute(
            select(Profile).order_by(Profile.id).limit(1)
        )
        return result.scalar_one_or_none()

    async def set_active(self, profile_id: UUID) -> Profile | None:
        await self.session.execute(
            update(Profile).values(is_active=False)
        )
        profile = await self.get_by_id(profile_id)
        if profile:
            profile.is_active = True
            await self.session.flush()
        return profile

    async def delete(self, profile_id: UUID) -> bool:
        profile = await self.get_by_id(profile_id)
        if profile:
            await self.session.delete(profile)
            await self.session.flush()
            return True
        return False

    async def update_settings(self, profile_id: UUID, **kwargs: Any) -> Profile | None:
        profile = await self.get_by_id(profile_id)
        if profile:
            for key, value in kwargs.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)
            await self.session.flush()
        return profile


class CycleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, profile_id: UUID, start_date: date) -> Cycle:
        cycle = Cycle(profile_id=profile_id, start_date=start_date)
        self.session.add(cycle)
        await self.session.flush()
        return cycle

    async def get_or_create_current(self, profile_id: UUID) -> Cycle:
        result = await self.session.execute(
            select(Cycle)
            .where(Cycle.profile_id == profile_id, Cycle.end_date == None)
            .order_by(Cycle.start_date.desc())
            .limit(1)
        )
        cycle = result.scalar_one_or_none()
        if cycle:
            return cycle
        return await self.create(profile_id, date.today())

    async def close_cycle(
        self, cycle_id: UUID, end_date: date, profile_id: UUID | None = None
    ) -> Cycle | None:
        stmt = select(Cycle).where(Cycle.id == cycle_id)
        if profile_id is not None:
            stmt = stmt.where(Cycle.profile_id == profile_id)
        result = await self.session.execute(stmt)
        cycle = result.scalar_one_or_none()
        if cycle:
            cycle.end_date = end_date
            delta = end_date - cycle.start_date
            cycle.cycle_length = delta.days or 1
            await self.session.flush()
        return cycle

    async def get_by_profile(self, profile_id: UUID) -> list[Cycle]:
        result = await self.session.execute(
            select(Cycle)
            .where(Cycle.profile_id == profile_id)
            .order_by(Cycle.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, cycle_id: UUID, profile_id: UUID | None = None) -> Cycle | None:
        stmt = select(Cycle).where(Cycle.id == cycle_id)
        if profile_id is not None:
            stmt = stmt.where(Cycle.profile_id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_past_lengths(self, profile_id: UUID, limit: int = 6) -> list[int]:
        result = await self.session.execute(
            select(Cycle.cycle_length)
            .where(
                Cycle.profile_id == profile_id,
                Cycle.cycle_length != None,
                Cycle.end_date != None,
            )
            .order_by(Cycle.start_date.desc())
            .limit(limit)
        )
        lengths = result.scalars().all()
        return [int(length) for length in lengths if length is not None]


class EntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_temperature(
        self,
        cycle_id: UUID,
        entry_date: date,
        temp_value: float,
        time_taken: Any = None,
        is_discarded: bool = False,
        discard_reason: str = "",
        notes: str = "",
    ) -> Temperature:
        result = await self.session.execute(
            select(Temperature).where(
                Temperature.cycle_id == cycle_id, Temperature.date == entry_date
            )
        )
        temp = result.scalar_one_or_none()
        if temp:
            temp.temp_value = temp_value
            if time_taken is not None:
                temp.time_taken = time_taken
            temp.is_discarded = is_discarded
            temp.discard_reason = discard_reason
            temp.notes = notes
        else:
            temp = Temperature(
                cycle_id=cycle_id,
                date=entry_date,
                temp_value=temp_value,
                time_taken=time_taken,
                is_discarded=is_discarded,
                discard_reason=discard_reason,
                notes=notes,
            )
            self.session.add(temp)
        await self.session.flush()
        return temp

    async def upsert_signs(
        self,
        cycle_id: UUID,
        entry_date: date,
        **kwargs: str,
    ) -> FertilitySigns:
        result = await self.session.execute(
            select(FertilitySigns).where(
                FertilitySigns.cycle_id == cycle_id, FertilitySigns.date == entry_date
            )
        )
        signs = result.scalar_one_or_none()
        if signs:
            for key, value in kwargs.items():
                if hasattr(signs, key):
                    setattr(signs, key, value)
        else:
            signs = FertilitySigns(cycle_id=cycle_id, date=entry_date, **kwargs)
            self.session.add(signs)
        await self.session.flush()
        return signs

    async def upsert_symptoms(
        self,
        cycle_id: UUID,
        entry_date: date,
        symptoms: list[dict[str, Any]],
    ) -> list[Symptom]:
        await self.session.execute(
            delete(Symptom).where(
                Symptom.cycle_id == cycle_id, Symptom.date == entry_date
            )
        )
        models: list[Symptom] = []
        for s in symptoms:
            symptom = Symptom(
                cycle_id=cycle_id,
                date=entry_date,
                symptom_type=str(s.get("symptom_type", "")),
                severity=int(s.get("severity", 1)),
            )
            self.session.add(symptom)
            models.append(symptom)
        await self.session.flush()
        return models

    async def get_temperature(
        self, cycle_id: UUID, entry_date: date
    ) -> Temperature | None:
        result = await self.session.execute(
            select(Temperature).where(
                Temperature.cycle_id == cycle_id, Temperature.date == entry_date
            )
        )
        return result.scalar_one_or_none()

    async def get_signs(
        self, cycle_id: UUID, entry_date: date
    ) -> FertilitySigns | None:
        result = await self.session.execute(
            select(FertilitySigns).where(
                FertilitySigns.cycle_id == cycle_id,
                FertilitySigns.date == entry_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_recent_temps(
        self, cycle_id: UUID, limit: int = 14
    ) -> list[Temperature]:
        result = await self.session.execute(
            select(Temperature)
            .where(Temperature.cycle_id == cycle_id)
            .order_by(Temperature.date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_temps_for_cycle(self, cycle_id: UUID) -> list[Temperature]:
        result = await self.session.execute(
            select(Temperature)
            .where(Temperature.cycle_id == cycle_id)
            .order_by(Temperature.date.asc())
        )
        return list(result.scalars().all())

    async def get_signs_for_cycle(self, cycle_id: UUID) -> list[FertilitySigns]:
        result = await self.session.execute(
            select(FertilitySigns)
            .where(FertilitySigns.cycle_id == cycle_id)
            .order_by(FertilitySigns.date.asc())
        )
        return list(result.scalars().all())

    async def get_symptoms_for_cycle(self, cycle_id: UUID) -> list[Symptom]:
        result = await self.session.execute(
            select(Symptom)
            .where(Symptom.cycle_id == cycle_id)
            .order_by(Symptom.date.asc(), Symptom.symptom_type.asc())
        )
        return list(result.scalars().all())


class InsightsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(
        self, cycle_id: UUID, insights_dict: dict[str, Any]
    ) -> ComputedInsights:
        result = await self.session.execute(
            select(ComputedInsights).where(
                ComputedInsights.cycle_id == cycle_id
            )
        )
        insights = result.scalar_one_or_none()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if insights:
            for key, value in insights_dict.items():
                if hasattr(insights, key):
                    setattr(insights, key, value)
            insights.computed_at = now
        else:
            insights = ComputedInsights(
                cycle_id=cycle_id,
                computed_at=now,
                **insights_dict,
            )
            self.session.add(insights)
        await self.session.flush()
        return insights

    async def get_for_cycle(self, cycle_id: UUID) -> ComputedInsights | None:
        result = await self.session.execute(
            select(ComputedInsights).where(
                ComputedInsights.cycle_id == cycle_id
            )
        )
        return result.scalar_one_or_none()


class ExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def export_profile(self, profile_id: UUID) -> dict[str, Any] | None:
        profile_result = await self.session.execute(
            select(Profile)
            .options(selectinload(Profile.cycles))
            .where(Profile.id == profile_id)
        )
        profile = profile_result.unique().scalar_one_or_none()
        if not profile:
            return None

        cycles_data: list[dict[str, Any]] = []
        for cycle in profile.cycles:
            temps_result = await self.session.execute(
                select(Temperature)
                .where(Temperature.cycle_id == cycle.id)
                .order_by(Temperature.date.asc())
            )
            signs_result = await self.session.execute(
                select(FertilitySigns)
                .where(FertilitySigns.cycle_id == cycle.id)
                .order_by(FertilitySigns.date.asc())
            )
            symptoms_result = await self.session.execute(
                select(Symptom)
                .where(Symptom.cycle_id == cycle.id)
                .order_by(Symptom.date.asc())
            )
            insights_result = await self.session.execute(
                select(ComputedInsights).where(
                    ComputedInsights.cycle_id == cycle.id
                )
            )
            cycles_data.append({
                "id": cycle.id,
                "start_date": cycle.start_date,
                "end_date": cycle.end_date,
                "cycle_length": cycle.cycle_length,
                "notes": cycle.notes,
                "temperatures": list(temps_result.scalars().all()),
                "fertility_signs": list(signs_result.scalars().all()),
                "symptoms": list(symptoms_result.scalars().all()),
                "insights": insights_result.scalar_one_or_none(),
            })

        return {
            "profile": profile,
            "cycles": cycles_data,
        }
