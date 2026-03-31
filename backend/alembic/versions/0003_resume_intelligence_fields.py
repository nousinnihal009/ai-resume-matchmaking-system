"""Add deep understanding fields to resumes table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deep understanding columns to resumes table
    # All nullable — existing resumes are unaffected
    op.add_column(
        "resumes",
        sa.Column("seniority_level", sa.String(50), nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("years_of_experience", sa.Float(), nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("career_trajectory", sa.String(100), nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("domain_expertise", JSONB, nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("impact_metrics", JSONB, nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("context_aware_skills", JSONB, nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("resume_analysis", JSONB, nullable=True)
    )
    op.add_column(
        "resumes",
        sa.Column("analysis_version", sa.String(20), nullable=True)
    )


def downgrade() -> None:
    for column in [
        "seniority_level", "years_of_experience", "career_trajectory",
        "domain_expertise", "impact_metrics", "context_aware_skills",
        "resume_analysis", "analysis_version",
    ]:
        op.drop_column("resumes", column)
