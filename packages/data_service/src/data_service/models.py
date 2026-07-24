from __future__ import annotations

from uuid import UUID, uuid4
from datetime import date, datetime, time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, UniqueConstraint, func


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    temp_unit: Mapped[str] = mapped_column(String(1), default="F")
    interpretation_method: Mapped[str] = mapped_column(
        String(16), default="standard"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), default=None)

    cycles: Mapped[list["Cycle"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name={self.name!r})>"


class Cycle(Base):
    __tablename__ = "cycles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    profile: Mapped["Profile"] = relationship(back_populates="cycles")
    temperatures: Mapped[list["Temperature"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )
    fertility_signs: Mapped[list["FertilitySigns"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )
    symptoms: Mapped[list["Symptom"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )
    computed_insight: Mapped["ComputedInsights | None"] = relationship(
        back_populates="cycle", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Cycle(id={self.id}, profile_id={self.profile_id}, start={self.start_date})>"


class Temperature(Base):
    __tablename__ = "temperatures"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("cycles.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(nullable=False)
    temp_value: Mapped[float] = mapped_column(Float, nullable=False)
    time_taken: Mapped[time | None] = mapped_column(nullable=True)
    is_discarded: Mapped[bool] = mapped_column(Boolean, default=False)
    discard_reason: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    __table_args__ = (UniqueConstraint("cycle_id", "date"),)

    cycle: Mapped["Cycle"] = relationship(back_populates="temperatures")

    def __repr__(self) -> str:
        return f"<Temperature(id={self.id}, date={self.date}, value={self.temp_value})>"


class FertilitySigns(Base):
    __tablename__ = "fertility_signs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("cycles.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(nullable=False)
    menstrual_flow: Mapped[str] = mapped_column(String(16), default="")
    cervical_mucus: Mapped[str] = mapped_column(String(16), default="")
    cervical_position: Mapped[str] = mapped_column(String(8), default="")
    cervical_firmness: Mapped[str] = mapped_column(String(8), default="")
    cervical_opening: Mapped[str] = mapped_column(String(8), default="")
    opk_result: Mapped[str] = mapped_column(String(16), default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    __table_args__ = (UniqueConstraint("cycle_id", "date"),)

    cycle: Mapped["Cycle"] = relationship(back_populates="fertility_signs")

    def __repr__(self) -> str:
        return f"<FertilitySigns(id={self.id}, date={self.date})>"


class Symptom(Base):
    __tablename__ = "symptoms"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("cycles.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(nullable=False)
    symptom_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[int] = mapped_column(Integer, default=1)

    cycle: Mapped["Cycle"] = relationship(back_populates="symptoms")

    def __repr__(self) -> str:
        return f"<Symptom(id={self.id}, type={self.symptom_type!r}, date={self.date})>"


class ComputedInsights(Base):
    __tablename__ = "computed_insights"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("cycles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    coverline: Mapped[float | None] = mapped_column(Float, nullable=True)
    ovulation_date: Mapped[date | None] = mapped_column(nullable=True)
    ovulation_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    ovulation_method: Mapped[str] = mapped_column(String(32), default="")
    fertile_start_date: Mapped[date | None] = mapped_column(nullable=True)
    fertile_end_date: Mapped[date | None] = mapped_column(nullable=True)
    post_ovulatory_infertile_date: Mapped[date | None] = mapped_column(nullable=True)
    luteal_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    luteal_phase_short: Mapped[bool] = mapped_column(Boolean, default=False)
    pregnancy_indicator: Mapped[bool] = mapped_column(Boolean, default=False)
    consecutive_elevated_temps: Mapped[int] = mapped_column(Integer, default=0)
    engine_version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    cycle: Mapped["Cycle"] = relationship(back_populates="computed_insight")

    def __repr__(self) -> str:
        return f"<ComputedInsights(id={self.id}, cycle_id={self.cycle_id})>"
