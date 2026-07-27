"""symptom_catalog_and_medications

Revision ID: 003
Revises: 002
Create Date: 2026-07-26
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Table, MetaData

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEED_SYMPTOMS = [
    {"name": "Cramps", "category": "pain", "severity_scale": 3},
    {"name": "Headache", "category": "pain", "severity_scale": 3},
    {"name": "Back Pain", "category": "pain", "severity_scale": 3},
    {"name": "Breast Tenderness", "category": "pain", "severity_scale": 3},
    {"name": "Ovulation Pain", "category": "pain", "severity_scale": 3},
    {"name": "Bloating", "category": "digestive", "severity_scale": 3},
    {"name": "Nausea", "category": "digestive", "severity_scale": 3},
    {"name": "Constipation", "category": "digestive", "severity_scale": 3},
    {"name": "Diarrhea", "category": "digestive", "severity_scale": 3},
    {"name": "Food Cravings", "category": "digestive", "severity_scale": 3},
    {"name": "Irritability", "category": "mood", "severity_scale": 3},
    {"name": "Anxiety", "category": "mood", "severity_scale": 3},
    {"name": "Depression", "category": "mood", "severity_scale": 3},
    {"name": "Mood Swings", "category": "mood", "severity_scale": 3},
    {"name": "Fatigue", "category": "energy", "severity_scale": 3},
    {"name": "Insomnia", "category": "energy", "severity_scale": 3},
    {"name": "High Energy", "category": "energy", "severity_scale": 3},
    {"name": "Low Energy", "category": "energy", "severity_scale": 3},
    {"name": "Acne", "category": "skin", "severity_scale": 3},
    {"name": "Dry Skin", "category": "skin", "severity_scale": 3},
    {"name": "Oily Skin", "category": "skin", "severity_scale": 3},
    {"name": "Spotting", "category": "other", "severity_scale": 3},
    {"name": "Hot Flashes", "category": "other", "severity_scale": 3},
    {"name": "Dizziness", "category": "other", "severity_scale": 3},
]


def upgrade() -> None:
    op.create_table(
        "symptom_catalog",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("severity_scale", sa.Integer(), nullable=False, server_default="3"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "medications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "profile_id",
            sa.Uuid(),
            sa.ForeignKey("profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("dosage", sa.String(40), nullable=True),
        sa.Column("schedule", sa.String(20), nullable=False, server_default="as_needed"),
        sa.Column(
            "taken_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    symptom_catalog = Table(
        "symptom_catalog",
        MetaData(),
        sa.Column("name", sa.String(80)),
        sa.Column("category", sa.String(80)),
        sa.Column("severity_scale", sa.Integer()),
    )
    op.bulk_insert(symptom_catalog, SEED_SYMPTOMS)


def downgrade() -> None:
    op.drop_table("medications")
    op.drop_table("symptom_catalog")
