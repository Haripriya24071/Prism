"""backend/config.py — Centralised application configuration and environment settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # GCP Project & Authentication (Vertex AI ADC)
    GCP_PROJECT_ID: str = "your-gcp-project-id"
    GCP_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Cloud Persistence
    GCS_BUCKET_NAME: str = "prism-sessions"
    BIGQUERY_DATASET: str = "prism_data"

    # Gemini Models via Vertex AI SDK
    GEMINI_FLASH_MODEL: str = "gemini-2.0-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"

    # External Context Harvester Keys
    NEWSAPI_KEY: str = ""
    CRUNCHBASE_KEY: str = ""

    # App & Server Settings
    CORS_ORIGINS: str = "http://localhost:5173"
    SESSION_TTL_SECONDS: int = 7200
    MAX_UPLOAD_BYTES: int = 10485760
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    # Timeouts (in seconds)
    HARVESTER_TIMEOUT_SECONDS: float = 8.0
    SWARM_TIMEOUT_SECONDS: float = 30.0
    EVALUATOR_TIMEOUT_SECONDS: float = 20.0

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
