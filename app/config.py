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
    gemini_generation_model: str = "gemini-3.5-flash"
    gemini_fast_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_timeout_ms: int = 30000
    gemini_retry_attempts: int = 2
    gemini_parse_retries: int = 1

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

    # Local embeddings (Phase 2 - open source)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimension: int = 384
    knowledge_docx_path: str = "knowledge-base/Student-Policy-knowledge-base.docx"
    bm25_cache_path: str = "data/evaluation/bm25_corpus.json"
    ingest_manifest_path: str = "data/evaluation/ingest_manifest.json"

    # Router (Phase 4)
    router_dataset_path: str = "knowledge-base/Student-dataset.csv"
    router_regression_path: str = "data/evaluation/router_regression_500.json"
    router_confidence_threshold: float = 0.70
    router_regression_per_intent: int = 25
    router_regression_seed: int = 42
    router_eval_report_path: str = "data/evaluation/router_eval_report.json"
    router_eval_delay_seconds: float = 12.0

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
