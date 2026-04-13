"""Add comprehensive resume analysis fields

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-18
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = [
        ("analysis_score", sa.Integer, {}),
        ("analysis_score_breakdown", JSON, {}),
        ("ats_parse_rate", sa.Float, {}),
        ("repetition_issues", JSON, {}),
        ("spelling_issues", JSON, {}),
        ("grammar_issues", JSON, {}),
        ("missing_sections", JSON, {}),
        ("present_sections", JSON, {}),
        ("contact_info", JSON, {}),
        ("file_analysis", JSON, {}),
        ("design_score", sa.Integer, {}),
        ("design_feedback", JSON, {}),
        ("template_suggestions", JSON, {}),
        ("full_analysis_report", JSON, {}),
        ("analysis_completed_at", sa.DateTime(timezone=True), {}),
    ]
    for col_name, col_type, kwargs in columns:
        op.add_column(
            "resumes",
            sa.Column(col_name, col_type, nullable=True, **kwargs)
        )


def downgrade() -> None:
    cols = [
        "analysis_score", "analysis_score_breakdown", "ats_parse_rate",
        "repetition_issues", "spelling_issues", "grammar_issues",
        "missing_sections", "present_sections", "contact_info",
        "file_analysis", "design_score", "design_feedback",
        "template_suggestions", "full_analysis_report",
        "analysis_completed_at",
    ]
    for col in cols:
        op.drop_column("resumes", col)
