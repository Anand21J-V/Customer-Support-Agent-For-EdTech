"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the student support AI service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini
    gemini_api_key: str = ""
    gemini_generation_model: str = "gemini-3.6-flash"
    gemini_fast_model: str = "gemini-3.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-2"

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "student_support"
    mysql_user: str = "student_ai"
    mysql_password: str = ""

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "student_support_knowledge"

    # Retrieval
    top_k_vector: int = 10
    top_k_bm25: int = 10
    top_k_final: int = 5

    # LangSmith
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "student-support-ai"

    # App
    log_level: str = "INFO"
    service_name: str = "student-support-ai-for-edtech"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
