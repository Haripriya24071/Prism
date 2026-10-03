"""backend/gcp/storage.py — Google Cloud Storage read/write helpers."""

import asyncio
import json
import uuid
from typing import Any
from google.cloud import storage
from backend.config import settings
from backend.errors import StorageError

__all__ = ["write_json", "read_json", "write_pdf"]

_ALLOWED_JSON_FILENAMES: frozenset[str] = frozenset(
    {
        "intake_package",
        "agent_vc",
        "agent_lean",
        "agent_cto",
        "agent_ux",
        "agent_regulator",
        "agent_adversarial",
        "score_matrix",
        "merged_brd",
        "heatmap",
        "investor_readiness",
    }
)

_ALLOWED_PDF_VIEWS: frozenset[str] = frozenset(
    {
        "investor",
        "technical",
        "regulatory",
    }
)

_client: storage.Client | None = None
_bucket: storage.Bucket | None = None


def _get_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client(project=settings.GCP_PROJECT_ID)
    return _client


def _get_bucket() -> storage.Bucket:
    global _bucket
    if _bucket is None:
        client = _get_client()
        _bucket = client.bucket(settings.GCS_BUCKET_NAME)
    return _bucket


def _validate_session_id(session_id: str) -> str:
    try:
        parsed_uuid = uuid.UUID(str(session_id))
        return str(parsed_uuid).lower()
    except (ValueError, TypeError, AttributeError):
        raise StorageError("Storage operation failed", detail="Invalid session ID")


def _validate_json_filename(filename: str) -> str:
    if not isinstance(filename, str):
        raise StorageError("Storage operation failed", detail="Invalid filename")
    name = filename[:-5] if filename.endswith(".json") else filename
    if name not in _ALLOWED_JSON_FILENAMES:
        raise StorageError("Storage operation failed", detail="Invalid filename")
    return name


def _validate_pdf_view(view: str) -> str:
    if not isinstance(view, str) or view not in _ALLOWED_PDF_VIEWS:
        raise StorageError("Storage operation failed", detail="Invalid view")
    return view


def _sync_write_json(session_id: str, name: str, data: dict[str, Any]) -> str:
    try:
        bucket = _get_bucket()
        blob_path = f"{session_id}/{name}.json"
        blob = bucket.blob(blob_path)
        payload = json.dumps(data)
        blob.upload_from_string(payload, content_type="application/json")
        if not blob.exists():
            raise StorageError("Storage operation failed", detail="Write confirmation failed")
        return f"gs://{settings.GCS_BUCKET_NAME}/{blob_path}"
    except StorageError:
        raise
    except Exception as exc:
        raise StorageError("Storage operation failed", detail=type(exc).__name__) from exc


def _sync_read_json(session_id: str, name: str) -> dict[str, Any] | None:
    try:
        bucket = _get_bucket()
        blob_path = f"{session_id}/{name}.json"
        blob = bucket.blob(blob_path)
        if not blob.exists():
            return None
        content = blob.download_as_text()
        return json.loads(content)
    except StorageError:
        raise
    except Exception as exc:
        raise StorageError("Storage operation failed", detail=type(exc).__name__) from exc


def _sync_write_pdf(session_id: str, view: str, pdf_bytes: bytes) -> str:
    try:
        bucket = _get_bucket()
        blob_path = f"{session_id}/output_{view}.pdf"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        if not blob.exists():
            raise StorageError("Storage operation failed", detail="Write confirmation failed")
        return f"gs://{settings.GCS_BUCKET_NAME}/{blob_path}"
    except StorageError:
        raise
    except Exception as exc:
        raise StorageError("Storage operation failed", detail=type(exc).__name__) from exc


async def write_json(session_id: str, filename: str, data: dict) -> str:
    valid_session_id = _validate_session_id(session_id)
    name = _validate_json_filename(filename)
    return await asyncio.to_thread(_sync_write_json, valid_session_id, name, data)


async def read_json(session_id: str, filename: str) -> dict | None:
    valid_session_id = _validate_session_id(session_id)
    name = _validate_json_filename(filename)
    return await asyncio.to_thread(_sync_read_json, valid_session_id, name)


async def write_pdf(session_id: str, filename: str, pdf_bytes: bytes, view: str) -> str:
    valid_session_id = _validate_session_id(session_id)
    valid_view = _validate_pdf_view(view)
    return await asyncio.to_thread(_sync_write_pdf, valid_session_id, valid_view, pdf_bytes)
