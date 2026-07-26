from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .encryption import ProfileEncryption
from .models import Cycle, Profile
from .repositories import (
    CycleRepository,
    EntryRepository,
    ExportRepository,
    InsightsRepository,
    ProfileRepository,
)
from .schemas import EntryCreate


class DataService:
    def __init__(self, session: AsyncSession, secret_key: str | None = None) -> None:
        self.session = session
        self._secret_key = secret_key
        self.profiles = ProfileRepository(session)
        self.cycles = CycleRepository(session)
        self.entries = EntryRepository(session)
        self.insights_repo = InsightsRepository(session)
        self.exports = ExportRepository(session)

    def entries_for(self, profile_id: UUID) -> EntryRepository:
        if self._secret_key:
            return EntryRepository(self.session, ProfileEncryption(self._secret_key, str(profile_id)))
        return self.entries

    def _encrypted_exports(self, profile_id: UUID) -> ExportRepository:
        if self._secret_key:
            return ExportRepository(self.session, ProfileEncryption(self._secret_key, str(profile_id)))
        return self.exports

    async def create_profile(
        self, name: str, temp_unit: str = "F"
    ) -> Profile:
        return await self.profiles.create(name, temp_unit)

    async def get_active_profile(self) -> Profile | None:
        return await self.profiles.get_active()

    async def log_entry(
        self, profile_id: UUID, entry: EntryCreate
    ) -> None:
        cycle = await self.cycles.get_or_create_current(profile_id)
        entries = self.entries_for(profile_id)

        if entry.temp_value is not None:
            await entries.upsert_temperature(
                cycle_id=cycle.id,
                entry_date=entry.date,
                temp_value=entry.temp_value,
                time_taken=entry.time_taken,
            )

        if entry.signs:
            await entries.upsert_signs(
                cycle_id=cycle.id, entry_date=entry.date, **entry.signs
            )

        if entry.symptoms:
            await entries.upsert_symptoms(
                cycle_id=cycle.id,
                entry_date=entry.date,
                symptoms=entry.symptoms,
            )

    async def get_or_create_current_cycle(self, profile_id: UUID) -> Cycle:
        return await self.cycles.get_or_create_current(profile_id)

    async def save_insights(
        self, cycle_id: UUID, insights: dict
    ) -> None:
        await self.insights_repo.upsert(cycle_id, insights)

    async def get_insights(self, cycle_id: UUID) -> dict | None:
        insights = await self.insights_repo.get_for_cycle(cycle_id)
        if not insights:
            return None
        return {
            "id": insights.id,
            "cycle_id": insights.cycle_id,
            "coverline": insights.coverline,
            "ovulation_date": insights.ovulation_date,
            "ovulation_confirmed": insights.ovulation_confirmed,
            "ovulation_method": insights.ovulation_method,
            "fertile_start_date": insights.fertile_start_date,
            "fertile_end_date": insights.fertile_end_date,
            "post_ovulatory_infertile_date": insights.post_ovulatory_infertile_date,
            "luteal_length": insights.luteal_length,
            "luteal_phase_short": insights.luteal_phase_short,
            "pregnancy_indicator": insights.pregnancy_indicator,
            "consecutive_elevated_temps": insights.consecutive_elevated_temps,
            "engine_version": insights.engine_version,
            "computed_at": insights.computed_at,
        }

    async def export_profile_data(self, profile_id: UUID) -> dict | None:
        exports = self._encrypted_exports(profile_id)
        return await exports.export_profile(profile_id)
