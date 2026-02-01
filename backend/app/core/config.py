"""
Core configuration for the FastAPI application.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, Field


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

    # JWT
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File Upload
    upload_directory: str = Field(default="./uploads", env="UPLOAD_DIRECTORY")
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_extensions: List[str] = [".pdf", ".docx"]

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )

    # ML Pipeline
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = 384

    # External Services (placeholders)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
