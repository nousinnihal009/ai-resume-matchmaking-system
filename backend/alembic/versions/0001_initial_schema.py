"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-17
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── CREATE TABLES (in foreign key dependency order) ──────────────

    # 1. users (no FK dependencies)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint("role IN ('student', 'recruiter', 'admin')", name="check_user_role"),
    )

    # 2. student_profiles (FK → users)
    op.create_table(
        "student_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("university", sa.String(255), nullable=True),
        sa.Column("major", sa.String(255), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # 3. recruiter_profiles (FK → users)
    op.create_table(
        "recruiter_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("position", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # 4. resumes (FK → users)
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("extracted_skills", postgresql.JSONB(), server_default="[]"),
        sa.Column("education", postgresql.JSONB(), server_default="[]"),
        sa.Column("experience", postgresql.JSONB(), server_default="[]"),
        sa.Column("status", sa.String(20), server_default="processing"),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('processing', 'completed', 'failed')", name="check_resume_status"),
    )

    # 5. jobs (FK → users via recruiter_id)
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("recruiter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("required_skills", postgresql.JSONB(), server_default="[]"),
        sa.Column("preferred_skills", postgresql.JSONB(), server_default="[]"),
        sa.Column("experience_level", sa.String(20), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("location_type", sa.String(20), nullable=False),
        sa.Column("salary_min", sa.DECIMAL(10, 2), nullable=True),
        sa.Column("salary_max", sa.DECIMAL(10, 2), nullable=True),
        sa.Column("salary_currency", sa.String(3), server_default="USD"),
        sa.Column("posted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("experience_level IN ('internship', 'entry', 'mid', 'senior')", name="check_job_experience_level"),
        sa.CheckConstraint("location_type IN ('onsite', 'remote', 'hybrid')", name="check_job_location_type"),
        sa.CheckConstraint("status IN ('active', 'closed', 'draft')", name="check_job_status"),
    )

    # 6. embeddings (no FK — uses entity_id as logical reference)
    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("vector", postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column("dimension", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("entity_type IN ('resume', 'job')", name="check_embedding_entity_type"),
    )

    # 7. matches (FK → resumes, jobs, users x2)
    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recruiter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.DECIMAL(5, 4), nullable=False),
        sa.Column("skill_score", sa.DECIMAL(5, 4), nullable=False),
        sa.Column("experience_score", sa.DECIMAL(5, 4), nullable=False),
        sa.Column("semantic_score", sa.DECIMAL(5, 4), nullable=False),
        sa.Column("matched_skills", postgresql.JSONB(), server_default="[]"),
        sa.Column("missing_skills", postgresql.JSONB(), server_default="[]"),
        sa.Column("explanation", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("overall_score >= 0 AND overall_score <= 1", name="check_match_overall_score"),
        sa.CheckConstraint("status IN ('pending', 'viewed', 'shortlisted', 'rejected')", name="check_match_status"),
    )

    # 8. match_history (FK → matches, users)
    op.create_table(
        "match_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("previous_status", sa.String(20), nullable=True),
        sa.Column("new_status", sa.String(20), nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # 9. analytics_events (FK → users with SET NULL)
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── CREATE INDEXES ───────────────────────────────────────────────

    # users indexes
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])

    # student_profiles indexes
    op.create_index("idx_student_profiles_user_id", "student_profiles", ["user_id"])

    # recruiter_profiles indexes
    op.create_index("idx_recruiter_profiles_user_id", "recruiter_profiles", ["user_id"])

    # resumes indexes
    op.create_index("idx_resumes_user_id", "resumes", ["user_id"])
    op.create_index("idx_resumes_status", "resumes", ["status"])
    op.create_index("idx_resumes_extracted_skills", "resumes", ["extracted_skills"], postgresql_using="gin")

    # jobs indexes
    op.create_index("idx_jobs_recruiter_id", "jobs", ["recruiter_id"])
    op.create_index("idx_jobs_status", "jobs", ["status"])
    op.create_index("idx_jobs_required_skills", "jobs", ["required_skills"], postgresql_using="gin")
    op.create_index("idx_jobs_experience_level", "jobs", ["experience_level"])

    # embeddings indexes
    op.create_index("idx_embeddings_entity", "embeddings", ["entity_id", "entity_type"], unique=True)

    # matches indexes
    op.create_index("idx_matches_resume_id", "matches", ["resume_id"])
    op.create_index("idx_matches_job_id", "matches", ["job_id"])
    op.create_index("idx_matches_student_id", "matches", ["student_id"])
    op.create_index("idx_matches_recruiter_id", "matches", ["recruiter_id"])
    op.create_index("idx_matches_overall_score", "matches", ["overall_score"])
    op.create_index("idx_matches_status", "matches", ["status"])

    # match_history indexes
    op.create_index("idx_match_history_match_id", "match_history", ["match_id"])

    # analytics_events indexes
    op.create_index("idx_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("idx_analytics_events_type", "analytics_events", ["event_type"])
    op.create_index("idx_analytics_events_created_at", "analytics_events", ["created_at"])


def downgrade() -> None:
    # ── DROP INDEXES (reverse order) ─────────────────────────────────

    # analytics_events indexes
    op.drop_index("idx_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("idx_analytics_events_type", table_name="analytics_events")
    op.drop_index("idx_analytics_events_user_id", table_name="analytics_events")

    # match_history indexes
    op.drop_index("idx_match_history_match_id", table_name="match_history")

    # matches indexes
    op.drop_index("idx_matches_status", table_name="matches")
    op.drop_index("idx_matches_overall_score", table_name="matches")
    op.drop_index("idx_matches_recruiter_id", table_name="matches")
    op.drop_index("idx_matches_student_id", table_name="matches")
    op.drop_index("idx_matches_job_id", table_name="matches")
    op.drop_index("idx_matches_resume_id", table_name="matches")

    # embeddings indexes
    op.drop_index("idx_embeddings_entity", table_name="embeddings")

    # jobs indexes
    op.drop_index("idx_jobs_experience_level", table_name="jobs")
    op.drop_index("idx_jobs_required_skills", table_name="jobs")
    op.drop_index("idx_jobs_status", table_name="jobs")
    op.drop_index("idx_jobs_recruiter_id", table_name="jobs")

    # resumes indexes
    op.drop_index("idx_resumes_extracted_skills", table_name="resumes")
    op.drop_index("idx_resumes_status", table_name="resumes")
    op.drop_index("idx_resumes_user_id", table_name="resumes")

    # recruiter_profiles indexes
    op.drop_index("idx_recruiter_profiles_user_id", table_name="recruiter_profiles")

    # student_profiles indexes
    op.drop_index("idx_student_profiles_user_id", table_name="student_profiles")

    # users indexes
    op.drop_index("idx_users_role", table_name="users")
    op.drop_index("idx_users_email", table_name="users")

    # ── DROP TABLES (reverse dependency order) ───────────────────────

    op.drop_table("analytics_events")
    op.drop_table("match_history")
    op.drop_table("matches")
    op.drop_table("embeddings")
    op.drop_table("jobs")
    op.drop_table("resumes")
    op.drop_table("recruiter_profiles")
    op.drop_table("student_profiles")
    op.drop_table("users")

