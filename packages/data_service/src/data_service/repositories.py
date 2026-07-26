from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .encryption import ProfileEncryption
from .models import ComputedInsights, Cycle, FertilitySigns, Profile, Symptom, Temperature


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
    def __init__(self, session: AsyncSession, encryption: ProfileEncryption | None = None) -> None:
        self.session = session
        self._encryption = encryption

    def _encrypt_field(self, value: str | float | None) -> str | None:
        if value is None:
            return None
        if self._encryption:
            return self._encryption.encrypt(value)
        return str(value) if isinstance(value, float) else value

    def _decrypt_field(self, value: str | float | None) -> str | float | None:
        if value is None:
            return None
        if not self._encryption:
            return value
        # Legacy: database may contain plaintext values (float or short strings)
        # from before encryption was enabled. Skip decryption for non-encrypted data.
        if isinstance(value, (int, float)):
            return value
        try:
            return self._encryption.decrypt(str(value))
        except Exception:
            # Value is not valid encrypted ciphertext — return as plaintext
            return value

    def _decrypt_temp_value(self, t: Temperature) -> None:
        decrypted = self._decrypt_field(t.temp_value)
        t.temp_value = float(decrypted) if decrypted else 0.0
        t.discard_reason = self._decrypt_field(t.discard_reason) or ""
        t.notes = self._decrypt_field(t.notes)

    def _decrypt_signs_fields(self, s: FertilitySigns) -> None:
        for field in ("menstrual_flow", "cervical_mucus", "cervical_position",
                      "cervical_firmness", "cervical_opening", "opk_result", "notes"):
            current = getattr(s, field, None)
            if current is not None:
                setattr(s, field, self._decrypt_field(current))

    def _decrypt_symptom(self, s: Symptom) -> None:
        s.symptom_type = self._decrypt_field(s.symptom_type) or ""

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

        encrypted_temp = self._encrypt_field(temp_value)
        encrypted_notes = self._encrypt_field(notes) if notes else None
        encrypted_reason = self._encrypt_field(discard_reason) if discard_reason else None

        if temp:
            temp.temp_value = encrypted_temp
            if time_taken is not None:
                temp.time_taken = time_taken
            temp.is_discarded = is_discarded
            temp.discard_reason = encrypted_reason
            temp.notes = encrypted_notes
        else:
            temp = Temperature(
                cycle_id=cycle_id,
                date=entry_date,
                temp_value=encrypted_temp,
                time_taken=time_taken,
                is_discarded=is_discarded,
                discard_reason=encrypted_reason,
                notes=encrypted_notes,
            )
            self.session.add(temp)
        await self.session.flush()

        temp.temp_value = temp_value
        temp.notes = notes if notes else None
        return temp

    async def upsert_signs(
        self,
        cycle_id: UUID,
        entry_date: date,
        **kwargs: str,
    ) -> FertilitySigns:
        encrypted_kwargs = {
            key: self._encrypt_field(value) if value is not None else None
            for key, value in kwargs.items()
        }

        result = await self.session.execute(
            select(FertilitySigns).where(
                FertilitySigns.cycle_id == cycle_id, FertilitySigns.date == entry_date
            )
        )
        signs = result.scalar_one_or_none()
        if signs:
            for key, value in encrypted_kwargs.items():
                if hasattr(signs, key):
                    setattr(signs, key, value)
        else:
            signs = FertilitySigns(cycle_id=cycle_id, date=entry_date, **encrypted_kwargs)
            self.session.add(signs)
        await self.session.flush()

        for key, value in kwargs.items():
            setattr(signs, key, value if value is not None else None)
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
            original_type = str(s.get("symptom_type", ""))
            symptom = Symptom(
                cycle_id=cycle_id,
                date=entry_date,
                symptom_type=self._encrypt_field(original_type),
                severity=int(s.get("severity", 1)),
            )
            self.session.add(symptom)
            models.append(symptom)
        await self.session.flush()

        for i, symptom in enumerate(models):
            symptom.symptom_type = symptoms[i].get("symptom_type", "")
        return models

    async def get_temperature(
        self, cycle_id: UUID, entry_date: date
    ) -> Temperature | None:
        result = await self.session.execute(
            select(Temperature).where(
                Temperature.cycle_id == cycle_id, Temperature.date == entry_date
            )
        )
        temp = result.scalar_one_or_none()
        if temp:
            self._decrypt_temp_value(temp)
        return temp

    async def get_signs(
        self, cycle_id: UUID, entry_date: date
    ) -> FertilitySigns | None:
        result = await self.session.execute(
            select(FertilitySigns).where(
                FertilitySigns.cycle_id == cycle_id,
                FertilitySigns.date == entry_date,
            )
        )
        signs = result.scalar_one_or_none()
        if signs:
            self._decrypt_signs_fields(signs)
        return signs

    async def get_recent_temps(
        self, cycle_id: UUID, limit: int = 14
    ) -> list[Temperature]:
        result = await self.session.execute(
            select(Temperature)
            .where(Temperature.cycle_id == cycle_id)
            .order_by(Temperature.date.desc())
            .limit(limit)
        )
        temps = list(result.scalars().all())
        for t in temps:
            self._decrypt_temp_value(t)
            t.notes = self._decrypt_field(t.notes)
        return temps

    async def get_temps_for_cycle(self, cycle_id: UUID) -> list[Temperature]:
        result = await self.session.execute(
            select(Temperature)
            .where(Temperature.cycle_id == cycle_id)
            .order_by(Temperature.date.asc())
        )
        temps = list(result.scalars().all())
        for t in temps:
            self._decrypt_temp_value(t)
            t.notes = self._decrypt_field(t.notes)
        return temps

    async def get_signs_for_cycle(self, cycle_id: UUID) -> list[FertilitySigns]:
        result = await self.session.execute(
            select(FertilitySigns)
            .where(FertilitySigns.cycle_id == cycle_id)
            .order_by(FertilitySigns.date.asc())
        )
        signs_list = list(result.scalars().all())
        for s in signs_list:
            self._decrypt_signs_fields(s)
        return signs_list

    async def get_symptoms_for_cycle(self, cycle_id: UUID) -> list[Symptom]:
        result = await self.session.execute(
            select(Symptom)
            .where(Symptom.cycle_id == cycle_id)
            .order_by(Symptom.date.asc(), Symptom.symptom_type.asc())
        )
        symptoms = list(result.scalars().all())
        for s in symptoms:
            self._decrypt_symptom(s)
        return symptoms


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
        now = datetime.now(UTC).replace(tzinfo=None)
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
    def __init__(self, session: AsyncSession, encryption: ProfileEncryption | None = None) -> None:
        self.session = session
        self._encryption = encryption

    def _decrypt_temp_value(self, t: Temperature) -> None:
        if self._encryption is None:
            t.temp_value = float(t.temp_value) if t.temp_value else 0.0
            return
        decrypted = self._encryption.decrypt(t.temp_value)
        t.temp_value = float(decrypted) if decrypted else 0.0
        t.discard_reason = self._encryption.decrypt(t.discard_reason) if t.discard_reason else ""
        t.notes = self._encryption.decrypt(t.notes) if t.notes else None

    def _decrypt_signs_fields(self, s: FertilitySigns) -> None:
        for field in ("menstrual_flow", "cervical_mucus", "cervical_position",
                      "cervical_firmness", "cervical_opening", "opk_result", "notes"):
            current = getattr(s, field, None)
            if current is not None and self._encryption is not None:
                setattr(s, field, self._encryption.decrypt(current))

    def _decrypt_symptom(self, s: Symptom) -> None:
        if self._encryption is not None:
            s.symptom_type = self._encryption.decrypt(s.symptom_type) or ""

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
            temps = list(temps_result.scalars().all())
            signs_list = list(signs_result.scalars().all())
            symptoms = list(symptoms_result.scalars().all())

            for t in temps:
                self._decrypt_temp_value(t)

            for s in signs_list:
                self._decrypt_signs_fields(s)

            for s in symptoms:
                self._decrypt_symptom(s)

            cycles_data.append({
                "id": cycle.id,
                "start_date": cycle.start_date,
                "end_date": cycle.end_date,
                "cycle_length": cycle.cycle_length,
                "notes": cycle.notes,
                "temperatures": temps,
                "fertility_signs": signs_list,
                "symptoms": symptoms,
                "insights": insights_result.scalar_one_or_none(),
            })

        return {
            "profile": profile,
            "cycles": cycles_data,
        }
