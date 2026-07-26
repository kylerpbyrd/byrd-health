"""initial_schema

Revision ID: 001
Revises:
Create Date: 2026-07-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("temp_unit", sa.String(1), nullable=False, server_default="F"),
        sa.Column(
            "interpretation_method",
            sa.String(16),
            nullable=False,
            server_default="standard",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "cycles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "profile_id",
            sa.Uuid(),
            sa.ForeignKey("profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("cycle_length", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "temperatures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "cycle_id",
            sa.Uuid(),
            sa.ForeignKey("cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("temp_value", sa.Text(), nullable=False),
        sa.Column("time_taken", sa.Time(), nullable=True),
        sa.Column("is_discarded", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("discard_reason", sa.Text(), server_default="", nullable=False),
        sa.Column("notes", sa.Text(), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cycle_id", "date"),
    )

    op.create_table(
        "fertility_signs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "cycle_id",
            sa.Uuid(),
            sa.ForeignKey("cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("menstrual_flow", sa.String(16), server_default="", nullable=False),
        sa.Column("cervical_mucus", sa.String(16), server_default="", nullable=False),
        sa.Column("cervical_position", sa.String(8), server_default="", nullable=False),
        sa.Column("cervical_firmness", sa.String(8), server_default="", nullable=False),
        sa.Column("cervical_opening", sa.String(8), server_default="", nullable=False),
        sa.Column("opk_result", sa.String(16), server_default="", nullable=False),
        sa.Column("notes", sa.Text(), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cycle_id", "date"),
    )

    op.create_table(
        "symptoms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "cycle_id",
            sa.Uuid(),
            sa.ForeignKey("cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("symptom_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.Integer(), server_default="1", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "computed_insights",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "cycle_id",
            sa.Uuid(),
            sa.ForeignKey("cycles.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("coverline", sa.Float(), nullable=True),
        sa.Column("ovulation_date", sa.Date(), nullable=True),
        sa.Column(
            "ovulation_confirmed",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "ovulation_method",
            sa.String(32),
            server_default="",
            nullable=False,
        ),
        sa.Column("fertile_start_date", sa.Date(), nullable=True),
        sa.Column("fertile_end_date", sa.Date(), nullable=True),
        sa.Column("post_ovulatory_infertile_date", sa.Date(), nullable=True),
        sa.Column("luteal_length", sa.Integer(), nullable=True),
        sa.Column(
            "luteal_phase_short",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "pregnancy_indicator",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "consecutive_elevated_temps",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "engine_version",
            sa.String(16),
            server_default="1.0.0",
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("computed_insights")
    op.drop_table("symptoms")
    op.drop_table("fertility_signs")
    op.drop_table("temperatures")
    op.drop_table("cycles")
    op.drop_table("profiles")
