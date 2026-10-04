"""backend/config.py — Centralised application configuration, multi-key Gemini pool, and environment settings."""

import os
import sys
import types
import itertools
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
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

# Load environment files
load_dotenv(dotenv_path=_BACKEND_DIR / ".env")
load_dotenv(dotenv_path=_ROOT_DIR / ".env")
load_dotenv(dotenv_path=".env")


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
    def alphavantage_key(self) -> str:
        """Alias for ALPHAVANTAGE_KEY."""
        return self.ALPHAVANTAGE_KEY

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
            if not val:
                val = os.getenv(f"GEMINI_API_KEY_{i}") or os.getenv(f"GEMINI_KEY_{i}")
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


class KeyCircuitBreaker:
    """Intelligent circuit breaker and load balancer for Gemini API key pool.

    Maintains per-key and per-model health states, quarantining exhausted or rate-limited keys
    and dynamically routing traffic to healthy keys and models with zero downtime.
    State is persisted to /tmp/prism_key_health.json to survive server reloads.
    """

    _STATE_CACHE_FILE = Path("/tmp/prism_key_health.json")

    def __init__(self, key_pool: List[str]):
        self.key_pool = key_pool if key_pool else [""]
        self._lock = threading.Lock()
        self._index = 0
        self._states: Dict[str, Dict[str, Any]] = {
            k: {
                "key": k,
                "is_blacklisted": False,
                "consecutive_errors": 0,
                "success_count": 0,
                "model_cooldowns": {},  # model_name -> cooldown_until (timestamp)
                "cached_client": None,
            }
            for k in self.key_pool
        }
        self._load_cached_state()

    def _load_cached_state(self) -> None:
        import json
        try:
            if self._STATE_CACHE_FILE.exists():
                data = json.loads(self._STATE_CACHE_FILE.read_text(encoding="utf-8"))
                now = time.time()
                for k, saved in data.items():
                    if k in self._states:
                        if saved.get("is_blacklisted"):
                            self._states[k]["is_blacklisted"] = True
                        for m_name, cd in saved.get("model_cooldowns", {}).items():
                            if cd > now:
                                self._states[k]["model_cooldowns"][m_name] = cd
                logger.info("gemini_health_cache_loaded", keys_cached=len(data))
        except Exception:
            pass

    def _save_cached_state(self) -> None:
        import json
        try:
            data = {}
            for k, s in self._states.items():
                data[k] = {
                    "is_blacklisted": s["is_blacklisted"],
                    "model_cooldowns": {m: cd for m, cd in s["model_cooldowns"].items() if cd > time.time()},
                }
            self._STATE_CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass

    def _get_client_for_key(self, key: str):
        from google.api_core import client_options
        import google.ai.generativelanguage as glm

        state = self._states.get(key)
        if state and state["cached_client"] is not None:
            return state["cached_client"]

        opts = client_options.ClientOptions(api_key=key)
        client = glm.GenerativeServiceClient(client_options=opts)
        if state:
            state["cached_client"] = client
        return client

    def acquire_candidate(self, preferred_models: List[str]) -> tuple[str, str, Any]:
        """Selects the best (key, model, client) triplet currently healthy.

        Returns (api_key, model_name, generative_service_client).
        """
        now = time.time()
        with self._lock:
            # 1. Look for a key & preferred model where key is not blacklisted and model is not on cooldown
            for model_name in preferred_models:
                # Rotate through keys starting from _index
                num_keys = len(self.key_pool)
                for i in range(num_keys):
                    idx = (self._index + i) % num_keys
                    key = self.key_pool[idx]
                    state = self._states.get(key)
                    if not state or state["is_blacklisted"]:
                        continue

                    cooldown = state["model_cooldowns"].get(model_name, 0.0)
                    if now >= cooldown:
                        self._index = (idx + 1) % num_keys
                        client = self._get_client_for_key(key)
                        return key, model_name, client

            # 2. If all models on all keys are on cooldown, find the (key, model) with earliest cooldown expiry
            best_key = self.key_pool[0]
            best_model = preferred_models[0]
            min_cooldown = float("inf")

            for key in self.key_pool:
                state = self._states.get(key)
                if not state or state["is_blacklisted"]:
                    continue
                for model_name in preferred_models:
                    cd = state["model_cooldowns"].get(model_name, 0.0)
                    if cd < min_cooldown:
                        min_cooldown = cd
                        best_key = key
                        best_model = model_name

            client = self._get_client_for_key(best_key)
            return best_key, best_model, client

    def record_success(self, key: str, model_name: str) -> None:
        with self._lock:
            state = self._states.get(key)
            if state:
                state["consecutive_errors"] = 0
                state["success_count"] += 1
                state["model_cooldowns"].pop(model_name, None)
                self._save_cached_state()

    def record_failure(self, key: str, model_name: str, error: Exception) -> None:
        err_str = str(error)
        now = time.time()

        with self._lock:
            state = self._states.get(key)
            if not state:
                return

            state["consecutive_errors"] += 1

            # Detect error category
            if any(term in err_str for term in ["401", "403", "API_KEY_INVALID", "invalid authentication credentials"]):
                state["is_blacklisted"] = True
                logger.error("gemini_key_blacklisted", key_prefix=key[:10], error=err_str[:120])
            elif "Please retry in" in err_str and ("h" in err_str or "d" in err_str or "seconds: 6" in err_str):
                # Daily quota exhaustion on this specific model
                state["model_cooldowns"][model_name] = now + 43200  # 12 hour quarantine
                logger.warning(
                    "gemini_daily_quota_quarantine",
                    key_prefix=key[:10],
                    model=model_name,
                    cooldown_hrs=12,
                )
            elif "429" in err_str or "ResourceExhausted" in err_str:
                # Short-term rate limit (e.g. 15 RPM)
                state["model_cooldowns"][model_name] = now + 60.0  # 60s cooldown
                logger.warning(
                    "gemini_rpm_cooldown",
                    key_prefix=key[:10],
                    model=model_name,
                    cooldown_sec=60,
                )
            elif any(code in err_str for code in ["503", "504", "Deadline", "Unavailable"]):
                state["model_cooldowns"][model_name] = now + 15.0  # 15s transient cooldown
            else:
                state["model_cooldowns"][model_name] = now + 10.0

            self._save_cached_state()


class RotatingGeminiChat:
    """Chat session wrapper that maintains conversation history and delegates to RotatingGeminiModel."""

    def __init__(self, model_wrapper: "RotatingGeminiModel", history: Optional[list] = None):
        self.model_wrapper = model_wrapper
        self.history = list(history) if history else []

    def send_message(self, message: Any, generation_config: Optional[Any] = None, **kwargs: Any) -> Any:
        if isinstance(message, str):
            current_content = Content(role="user", parts=[Part.from_text(message)])
        else:
            current_content = message

        full_contents = self.history + [current_content]
        response = self.model_wrapper.generate_content(
            full_contents,
            generation_config=generation_config,
            **kwargs,
        )
        self.history.append(current_content)
        if hasattr(response, "text"):
            self.history.append(Content(role="model", parts=[Part.from_text(response.text)]))
        return response


class RotatingGeminiModel:
    """A resilient, thread-safe wrapper around Gemini GenerativeModel with:

    1. Multi-key circuit breaking (quarantining exhausted keys, blacklisting invalid ones).
    2. Dynamic model cascading (e.g. flash-latest -> flash-lite -> gemini-flash-lite-latest) across separate quota pools.
    3. Thread-isolated client instances (preventing global state race conditions).
    """

    def __init__(self, model_name: str, key_pool: List[str]):
        self.model_name = model_name
        self.key_pool = key_pool if key_pool else [""]
        self.circuit_breaker = KeyCircuitBreaker(self.key_pool)

        # Build prioritized model fallback cascade
        if "pro" in model_name.lower():
            self.model_cascade = [
                model_name,
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
                "gemini-1.5-flash",
                "gemini-3.5-flash",
            ]
        else:
            self.model_cascade = [
                model_name,
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
                "gemini-1.5-flash",
                "gemini-3.5-flash",
            ]
        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped: List[str] = []
        for m in self.model_cascade:
            if m not in seen:
                seen.add(m)
                deduped.append(m)
        self.model_cascade = deduped

    def start_chat(self, history: Optional[list] = None) -> "RotatingGeminiChat":
        """Starts a chat session with full history support and circuit-broken rotation."""
        return RotatingGeminiChat(self, history=history)

    async def generate_content_async(self, contents: Any, generation_config: Optional[Any] = None, **kwargs: Any) -> Any:
        import asyncio
        return await asyncio.to_thread(self.generate_content, contents, generation_config=generation_config, **kwargs)

    def generate_content(self, contents: Any, generation_config: Optional[Any] = None, **kwargs: Any) -> Any:
        """Executes generation by rotating healthy keys and models with zero cross-thread locking."""
        last_exception = None
        max_attempts = min(20, max(6, len(self.key_pool) * 2))

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
            key, model_to_use, client_instance = self.circuit_breaker.acquire_candidate(self.model_cascade)
            try:
                model = genai.GenerativeModel(model_to_use)
                model._client = client_instance

                # Execute with explicit timeout options if not passed
                if "request_options" not in kwargs:
                    kwargs["request_options"] = {"timeout": 30}

                response = model.generate_content(
                    formatted_contents,
                    generation_config=generation_config,
                    **kwargs,
                )
                self.circuit_breaker.record_success(key, model_to_use)
                return response

            except Exception as e:
                err_msg = str(e)
                last_exception = e
                self.circuit_breaker.record_failure(key, model_to_use, e)
                logger.warning(
                    "gemini_request_fallback",
                    attempt=attempt + 1,
                    key_prefix=key[:10] if key else "empty",
                    model_tried=model_to_use,
                    error=err_msg[:120],
                )
                continue

        if last_exception:
            raise last_exception
        raise RuntimeError("All Gemini API keys and fallback models exhausted")


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
    """Returns Gemini Flash model with circuit breaker key rotation across all configured API keys."""
    global _flash_model_instance
    if _flash_model_instance is None:
        _flash_model_instance = RotatingGeminiModel(settings.gemini_flash_model, _KEYS)
    return _flash_model_instance


def get_pro_model() -> RotatingGeminiModel:
    """Returns Gemini Pro model with circuit breaker key rotation across all configured API keys."""
    global _pro_model_instance
    if _pro_model_instance is None:
        _pro_model_instance = RotatingGeminiModel(settings.gemini_pro_model, _KEYS)
    return _pro_model_instance
