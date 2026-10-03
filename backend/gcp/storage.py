"""backend/gcp/storage.py — Google Cloud Storage read/write helpers."""

import asyncio
import json
import os
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.config import settings
else:
    try:
        from backend.config import settings
    except ImportError:
        from config import settings

logger = structlog.get_logger()

_SIGNED_URL_EXPIRY = timedelta(hours=1)
_LOCAL_FALLBACK_DIR = Path("/tmp/prism-sessions")
_FALLBACK_DIR = _LOCAL_FALLBACK_DIR


def _get_client():
    """Returns GCS client. Import here to avoid module-level auth errors in dev."""
    from google.cloud import storage

    return storage.Client()


def _local_fallback_path(session_id: str, filename: str) -> Path:
    path = _FALLBACK_DIR / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


async def write_json(session_id: str, filename: str, data: dict) -> str:
    """Writes JSON data to GCS at bucket/{session_id}/{filename}.

    Falls back to /tmp/prism-sessions/{session_id}/{filename} in dev. Never raises — logs error and returns
    empty string on failure.
    """
    blob_path = f"{session_id}/{filename}"
    json_bytes = json.dumps(data, default=str).encode("utf-8")

    if not settings.gcs_bucket_name or settings.env == "development":
        try:
            local_path = _local_fallback_path(session_id, filename)
            local_path.write_bytes(json_bytes)
            logger.info("gcs_local_fallback_write", blob_path=blob_path, size=len(json_bytes))
            return f"local://{local_path}"
        except Exception as e:
            logger.warning("gcs_local_fallback_failed", error_type=type(e).__name__)
            return ""

    try:
        def _upload() -> str:
            client = _get_client()
            bucket = client.bucket(settings.gcs_bucket_name)
            blob = bucket.blob(blob_path)
            blob.upload_from_string(json_bytes, content_type="application/json")
            return f"gs://{settings.gcs_bucket_name}/{blob_path}"

        gcs_uri = await asyncio.to_thread(_upload)
        logger.info("gcs_write_ok", blob_path=blob_path, size=len(json_bytes))
        return gcs_uri
    except Exception as e:
        logger.error("gcs_write_failed", blob_path=blob_path, error_type=type(e).__name__)
        return ""


async def read_json(session_id: str, filename: str) -> dict | None:
    raise NotImplementedError()


async def write_pdf(session_id: str, filename: str, pdf_bytes: bytes, view: str) -> str:
    raise NotImplementedError()
