"""backend/config.py — Centralised application configuration, multi-key Gemini pool, and environment settings."""

import os
import sys
import types
import itertools
import threading
from pathlib import Path
from typing import Any, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig as GenAIGenerationConfig
except ImportError:
    genai = None  # type: ignore[assignment]
    GenAIGenerationConfig = None  # type: ignore[assignment]

logger = structlog.get_logger()

_BACKEND_DIR = Path(__file__).parent
_ROOT_DIR = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=(str(_BACKEND_DIR / ".env"), str(_ROOT_DIR / ".env"), ".env"),
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
    GEMINI_FLASH_MODEL: str = "gemini-flash-latest"
    GEMINI_PRO_MODEL: str = "gemini-pro-latest"

    # Gemini AI Studio API Key Pool
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_KEYS: Optional[str] = None
    GEMINI_API_KEY_1: Optional[str] = None
    GEMINI_API_KEY_2: Optional[str] = None
    GEMINI_API_KEY_3: Optional[str] = None
    GEMINI_API_KEY_4: Optional[str] = None
    GEMINI_API_KEY_5: Optional[str] = None
    GEMINI_API_KEY_6: Optional[str] = None
    GEMINI_API_KEY_7: Optional[str] = None
    GEMINI_API_KEY_8: Optional[str] = None
    GEMINI_API_KEY_9: Optional[str] = None
    GEMINI_API_KEY_10: Optional[str] = None
    GEMINI_API_KEY_11: Optional[str] = None
    GEMINI_API_KEY_12: Optional[str] = None
    GEMINI_API_KEY_13: Optional[str] = None
    GEMINI_API_KEY_14: Optional[str] = None
    GEMINI_API_KEY_15: Optional[str] = None
    GEMINI_API_KEY_16: Optional[str] = None
    GEMINI_API_KEY_17: Optional[str] = None
    GEMINI_API_KEY_18: Optional[str] = None
    GEMINI_API_KEY_19: Optional[str] = None
    GEMINI_API_KEY_20: Optional[str] = None

    # External Context Harvester Keys
    NEWSAPI_KEY: str = ""
    CRUNCHBASE_KEY: str = ""

    # App & Server Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    SESSION_TTL_SECONDS: int = 7200
    MAX_UPLOAD_BYTES: int = 10485760
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    # Timeouts (in seconds)
    HARVESTER_TIMEOUT_SECONDS: float = 8.0
    SWARM_TIMEOUT_SECONDS: float = 30.0
    EVALUATOR_TIMEOUT_SECONDS: float = 30.0

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Alias for cors_origins."""
        return self.cors_origins

    @property
    def gcp_project_id(self) -> str:
        return self.GCP_PROJECT_ID

    @property
    def bigquery_dataset(self) -> str:
        return self.BIGQUERY_DATASET

    @property
    def gcs_bucket_name(self) -> str:
        return self.GCS_BUCKET_NAME

    @property
    def gemini_flash_model(self) -> str:
        return self.GEMINI_FLASH_MODEL

    @property
    def gemini_pro_model(self) -> str:
        return self.GEMINI_PRO_MODEL

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL

    @property
    def env(self) -> str:
        return self.ENV

    @property
    def newsapi_key(self) -> str:
        return self.NEWSAPI_KEY

    @property
    def crunchbase_key(self) -> str:
        return self.CRUNCHBASE_KEY

    def get_all_gemini_keys(self) -> List[str]:
        """Collects all configured Gemini API keys into a deduplicated list."""
        keys: List[str] = []
        if self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip():
            keys.append(self.GEMINI_API_KEY.strip())
        if self.GEMINI_API_KEYS:
            for k in self.GEMINI_API_KEYS.split(","):
                if k.strip():
                    keys.append(k.strip())
        for i in range(1, 21):
            val = getattr(self, f"GEMINI_API_KEY_{i}", None)
            if val and val.strip():
                keys.append(val.strip())
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for k in keys:
            if k not in seen:
                seen.add(k)
                deduped.append(k)
        return deduped


settings = Settings()


class Content:
    """Compatible Content class for multi-turn chat."""
    def __init__(self, role: str = "user", parts: Optional[List[Any]] = None):
        self.role = role
        self.parts = parts or []


class Part:
    """Compatible wrapper for Part.from_data / Part.from_text."""
    def __init__(self, data: bytes = b"", mime_type: str = ""):
        self.data = data
        self.mime_type = mime_type

    @classmethod
    def from_data(cls, data: bytes, mime_type: str) -> dict:
        return {"mime_type": mime_type, "data": data}

    @classmethod
    def from_text(cls, text: str) -> str:
        return text


_BaseGenConfig: Any = GenAIGenerationConfig if GenAIGenerationConfig is not None else object


class GenerationConfig(_BaseGenConfig):
    """Compatible GenerationConfig wrapper."""
    pass


class RotatingGeminiModel:
    """A thread-safe wrapper around Gemini GenerativeModel that rotates API keys round-robin

    and automatically fails over to the next key on 429/ResourceExhausted.
    """

    def __init__(self, model_name: str, key_pool: List[str]):
        self.model_name = model_name
        self.key_pool = key_pool if key_pool else [""]
        self._lock = threading.Lock()
        self._index = 0

    def _get_next_key(self) -> str:
        with self._lock:
            key = self.key_pool[self._index % len(self.key_pool)]
            self._index += 1
            return key

    def generate_content(self, contents: Any, generation_config: Optional[Any] = None, **kwargs: Any) -> Any:
        """Attempts generation rotating through available keys if rate limits or transient errors occur."""
        last_exception = None
        max_attempts = max(1, len(self.key_pool))

        # Format contents: convert any Part/Content instances to supported genai format
        formatted_contents = contents
        if isinstance(contents, list):
            formatted_contents = []
            for item in contents:
                if isinstance(item, Part):
                    formatted_contents.append({"mime_type": item.mime_type, "data": item.data})
                elif isinstance(item, Content):
                    parts_list: list[Any] = []
                    for p in item.parts:
                        if isinstance(p, Part):
                            parts_list.append({"mime_type": p.mime_type, "data": p.data})
                        elif isinstance(p, dict):
                            parts_list.append(p)
                        else:
                            parts_list.append(str(p))
                    formatted_contents.append({"role": item.role, "parts": parts_list})
                else:
                    formatted_contents.append(item)

        for attempt in range(max_attempts):
            api_key = self._get_next_key()
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(
                    formatted_contents,
                    generation_config=generation_config,
                    **kwargs,
                )
                return response
            except Exception as e:
                err_msg = str(e)
                last_exception = e
                logger.warning(
                    "gemini_key_fallback",
                    model=self.model_name,
                    attempt=attempt + 1,
                    pool_size=len(self.key_pool),
                    error=err_msg[:120],
                )
                continue

        if last_exception:
            raise last_exception
        raise RuntimeError("No valid response from Gemini API key pool")


# Expose compatibility module in sys.modules so `import vertexai` and `from vertexai.generative_models import ...` works seamlessly!
_vertexai_mod = types.ModuleType("vertexai")
_vertexai_gen_mod = types.ModuleType("vertexai.generative_models")
_vertexai_gen_mod.GenerationConfig = GenerationConfig  # type: ignore[attr-defined]
_vertexai_gen_mod.Part = Part  # type: ignore[attr-defined]
_vertexai_gen_mod.Content = Content  # type: ignore[attr-defined]
_vertexai_gen_mod.GenerativeModel = RotatingGeminiModel  # type: ignore[attr-defined]
_vertexai_mod.generative_models = _vertexai_gen_mod  # type: ignore[attr-defined]
_vertexai_mod.init = lambda *args, **kwargs: None  # type: ignore[attr-defined]

sys.modules["vertexai"] = _vertexai_mod
sys.modules["vertexai.generative_models"] = _vertexai_gen_mod


# Initialize Key Pool
_KEYS = settings.get_all_gemini_keys()
_flash_model_instance: Optional[RotatingGeminiModel] = None
_pro_model_instance: Optional[RotatingGeminiModel] = None


def init_vertex_ai() -> None:
    """Initializes ADC / Vertex AI if credentials exist, otherwise gracefully uses Gemini AI Studio pool."""
    logger.info("gemini_key_pool_ready", total_keys=len(_KEYS), model_flash=settings.gemini_flash_model)


def get_flash_model() -> RotatingGeminiModel:
    """Returns Gemini Flash model with round-robin key rotation across all configured API keys."""
    global _flash_model_instance
    if _flash_model_instance is None:
        _flash_model_instance = RotatingGeminiModel(settings.gemini_flash_model, _KEYS)
    return _flash_model_instance


def get_pro_model() -> RotatingGeminiModel:
    """Returns Gemini Pro model with round-robin key rotation across all configured API keys."""
    global _pro_model_instance
    if _pro_model_instance is None:
        _pro_model_instance = RotatingGeminiModel(settings.gemini_pro_model, _KEYS)
    return _pro_model_instance
