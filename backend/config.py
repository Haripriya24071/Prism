"""backend/config.py — Centralised application configuration and environment settings."""

import itertools
import os
from typing import Any, List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from google import genai

# Load backend/.env and .env if present
load_dotenv(dotenv_path="backend/.env")
load_dotenv(dotenv_path=".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # GCP Project & Authentication
    GCP_PROJECT_ID: str = "prism-hackathon-510523"
    GCP_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Cloud Persistence
    GCS_BUCKET_NAME: str = "prism-outputs"
    BIGQUERY_DATASET: str = "prism_data"

    # Gemini Models
    GEMINI_FLASH_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_PRO_MODEL: str = "gemini-flash-lite-latest"

    # External Context Harvester Keys
    NEWSAPI_KEY: str = ""
    CRUNCHBASE_KEY: str = ""
    ALPHAVANTAGE_KEY: str = ""

    # App & Server Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    SESSION_TTL_SECONDS: int = 7200
    MAX_UPLOAD_BYTES: int = 10485760
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    # Timeouts (in seconds)
    HARVESTER_TIMEOUT_SECONDS: float = 8.0
    SWARM_TIMEOUT_SECONDS: float = 30.0
    EVALUATOR_TIMEOUT_SECONDS: float = 20.0

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Alias for cors_origins."""
        return self.cors_origins

    @property
    def gemini_flash_model(self) -> str:
        """Alias for GEMINI_FLASH_MODEL."""
        return self.GEMINI_FLASH_MODEL

    @property
    def gemini_pro_model(self) -> str:
        """Alias for GEMINI_PRO_MODEL."""
        return self.GEMINI_PRO_MODEL

    @property
    def alphavantage_key(self) -> str:
        """Alias for ALPHAVANTAGE_KEY."""
        return self.ALPHAVANTAGE_KEY

    @property
    def log_level(self) -> str:
        """Alias for LOG_LEVEL."""
        return self.LOG_LEVEL

    @property
    def env(self) -> str:
        """Alias for ENV."""
        return self.ENV


settings = Settings()


def _get_key_pool() -> list[str]:
    keys: list[str] = []
    # Check GEMINI_API_KEY_1..20
    for i in range(1, 21):
        k = os.getenv(f"GEMINI_API_KEY_{i}") or os.getenv(f"GEMINI_KEY_{i}")
        if k and k.strip():
            keys.append(k.strip())
    # Single fallback key
    single = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    if single and single.strip() and single.strip() not in keys:
        keys.append(single.strip())
    return keys


_KEY_POOL = _get_key_pool()
_key_cycle = itertools.cycle(_KEY_POOL) if _KEY_POOL else None


def _get_next_key() -> str:
    global _key_cycle, _KEY_POOL
    if not _KEY_POOL:
        _KEY_POOL = _get_key_pool()
        if _KEY_POOL:
            _key_cycle = itertools.cycle(_KEY_POOL)
    if not _key_cycle:
        return ""
    return next(_key_cycle)


class _ModelWrapper:
    """Wrapper that handles multi-key rotation and model fallback seamlessly."""

    def __init__(self, default_model: str):
        self.default_model = default_model

    def generate_content(self, prompt: str, generation_config: Any = None) -> Any:
        keys = _get_key_pool() or [""]
        models_to_try = [self.default_model, "gemini-flash-lite-latest", "gemini-1.5-flash"]
        last_exc: Optional[Exception] = None

        # Try across key pool
        for key in keys:
            try:
                client = genai.Client(api_key=key) if key else genai.Client()
                for m in models_to_try:
                    try:
                        return client.models.generate_content(model=m, contents=prompt)
                    except Exception as me:
                        last_exc = me
                        continue
            except Exception as e:
                last_exc = e
                continue

        if last_exc:
            raise last_exc


def init_vertex_ai() -> None:
    """No-op kept for backward compatibility."""
    pass


def get_flash_model() -> _ModelWrapper:
    """Returns Gemini Flash model with multi-key pool rotation."""
    return _ModelWrapper(settings.gemini_flash_model)


def get_pro_model() -> _ModelWrapper:
    """Returns Gemini Pro model with multi-key pool rotation."""
    return _ModelWrapper(settings.gemini_pro_model)
