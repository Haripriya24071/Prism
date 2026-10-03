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
    raise NotImplementedError()


async def read_json(session_id: str, filename: str) -> dict | None:
    raise NotImplementedError()


async def write_pdf(session_id: str, filename: str, pdf_bytes: bytes, view: str) -> str:
    raise NotImplementedError()
