"""
Core configuration for the FastAPI application.
"""
import json
import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "AI Resume Matching Platform"
    debug: bool = Field(default=False, env="DEBUG")
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/resume_matching",
        env="DATABASE_URL"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async engine."""
        if v and isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # JWT
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # File Upload
    upload_directory: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=5 * 1024 * 1024, env="MAX_UPLOAD_SIZE")
    allowed_extensions: List[str] = [".pdf", ".docx"]

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Accept JSON arrays or comma-separated CORS origins from env."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            value = v.strip()
            if not value:
                return ["http://localhost:3000", "http://localhost:5173"]
            if value.startswith("["):
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return v

    # ML Pipeline
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = 384
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")

    # External Services (placeholders)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
