"""
SQLAlchemy models mirroring the database schema.
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Float, DECIMAL, JSON, ForeignKey, CheckConstraint, Index, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback if pgvector is not available
    Vector = None

def _vector_column(dim):
    """Return Vector(dim) if pgvector is available, else ARRAY(Float)."""
    if Vector is not None:
        return Vector(dim)
    return ARRAY(Float)

Base = declarative_base()


class User(Base):
    """Users table model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    recruiter_profile = relationship("RecruiterProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    jobs = relationship("Job", back_populates="recruiter")

    __table_args__ = (
        CheckConstraint("role IN ('student', 'recruiter', 'admin')", name="check_user_role"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )


class StudentProfile(Base):
    """Student profiles table model."""
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    university = Column(String(255))
    major = Column(String(255))
    graduation_year = Column(Integer)
    phone_number = Column(String(20))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="student_profile")

    __table_args__ = (
        Index("idx_student_profiles_user_id", "user_id"),
    )


class RecruiterProfile(Base):
    """Recruiter profiles table model."""
    __tablename__ = "recruiter_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255))
    phone_number = Column(String(20))
    linkedin_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="recruiter_profile")

    __table_args__ = (
        Index("idx_recruiter_profiles_user_id", "user_id"),
    )


class Resume(Base):
    """Resumes table model."""
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    extracted_text = Column(Text)
    extracted_skills = Column(JSONB, server_default="[]")
    education = Column(JSONB, server_default="[]")
    experience = Column(JSONB, server_default="[]")
    status = Column(String(20), server_default="processing")
    extra_metadata = Column(JSONB, server_default="{}")
    
    # Deep understanding fields — populated by Gemini analysis
    seniority_level = Column(String(50), nullable=True)
    years_of_experience = Column(Float, nullable=True)
    career_trajectory = Column(String(100), nullable=True)
    domain_expertise = Column(JSONB, nullable=True)
    impact_metrics = Column(JSONB, nullable=True)
    context_aware_skills = Column(JSONB, nullable=True)
    resume_analysis = Column(JSONB, nullable=True)
    analysis_version = Column(String(20), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume")

    __table_args__ = (
        CheckConstraint("status IN ('processing', 'completed', 'failed')", name="check_resume_status"),
        Index("idx_resumes_user_id", "user_id"),
        Index("idx_resumes_status", "status"),
        Index("idx_resumes_extracted_skills", "extracted_skills", postgresql_using="gin"),
    )


class Job(Base):
    """Jobs table model."""
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSONB, server_default="[]")
    preferred_skills = Column(JSONB, server_default="[]")
    experience_level = Column(String(20), nullable=False)
    location = Column(String(255), nullable=False)
    location_type = Column(String(20), nullable=False)
    salary_min = Column(DECIMAL(10, 2))
    salary_max = Column(DECIMAL(10, 2))
    salary_currency = Column(String(3), server_default="USD")
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    status = Column(String(20), server_default="active")
    extra_metadata = Column(JSONB, server_default="{}")
    job_embedding_vector = Column(_vector_column(384), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    matches = relationship("Match", back_populates="job")

    __table_args__ = (
        CheckConstraint("experience_level IN ('internship', 'entry', 'mid', 'senior')", name="check_job_experience_level"),
        CheckConstraint("location_type IN ('onsite', 'remote', 'hybrid')", name="check_job_location_type"),
        CheckConstraint("status IN ('active', 'closed', 'draft')", name="check_job_status"),
        Index("idx_jobs_recruiter_id", "recruiter_id"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_required_skills", "required_skills", postgresql_using="gin"),
        Index("idx_jobs_experience_level", "experience_level"),
    )


class Embedding(Base):
    """Embeddings table model."""
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    entity_type = Column(String(20), nullable=False)
    vector = Column(_vector_column(384), nullable=False)
    dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("entity_type IN ('resume', 'job')", name="check_embedding_entity_type"),
        Index("idx_embeddings_entity", "entity_id", "entity_type", unique=True),
    )


class Match(Base):
    """Matches table model."""
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(DECIMAL(5, 4), nullable=False)
    skill_score = Column(DECIMAL(5, 4), nullable=False)
    experience_score = Column(DECIMAL(5, 4), nullable=False)
    semantic_score = Column(DECIMAL(5, 4), nullable=False)
    matched_skills = Column(JSONB, server_default="[]")
    missing_skills = Column(JSONB, server_default="[]")
    explanation = Column(JSONB, nullable=False)
    status = Column(String(20), server_default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")

    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 1", name="check_match_overall_score"),
        CheckConstraint("status IN ('pending', 'viewed', 'shortlisted', 'rejected')", name="check_match_status"),
        Index("idx_matches_resume_id", "resume_id"),
        Index("idx_matches_job_id", "job_id"),
        Index("idx_matches_student_id", "student_id"),
        Index("idx_matches_recruiter_id", "recruiter_id"),
        Index("idx_matches_overall_score", "overall_score"),
        Index("idx_matches_status", "status"),
    )


class MatchHistory(Base):
    """Match history table model."""
    __tablename__ = "match_history"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    previous_status = Column(String(20))
    new_status = Column(String(20))
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_match_history_match_id", "match_id"),
    )


class AnalyticsEvent(Base):
    """Analytics events table model."""
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_analytics_events_user_id", "user_id"),
        Index("idx_analytics_events_type", "event_type"),
        Index("idx_analytics_events_created_at", "created_at"),
    )
