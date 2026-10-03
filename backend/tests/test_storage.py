"""Tests for backend/gcp/storage.py."""

import json
from unittest.mock import MagicMock, patch
import pytest
from backend.errors import StorageError
from backend.gcp import storage

VALID_SESSION_ID = "12345678-1234-5678-1234-567812345678"
VALID_UPPER_SESSION_ID = "12345678-1234-5678-1234-567812345678".upper()


@pytest.fixture(autouse=True)
def reset_storage_globals():
    storage._client = None
    storage._bucket = None
    yield
    storage._client = None
    storage._bucket = None


@pytest.fixture
def mock_bucket():
    bucket = MagicMock()
    with patch("backend.gcp.storage._get_bucket", return_value=bucket):
        yield bucket


@pytest.mark.asyncio
async def test_write_json_success(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = True
    mock_bucket.blob.return_value = blob_mock

    data = {"score": 95, "status": "approved"}
    result = await storage.write_json(VALID_SESSION_ID, "merged_brd", data)

    expected_path = f"{VALID_SESSION_ID}/merged_brd.json"
    mock_bucket.blob.assert_called_once_with(expected_path)
    blob_mock.upload_from_string.assert_called_once_with(
        json.dumps(data),
        content_type="application/json",
    )
    blob_mock.exists.assert_called_once()
    assert result == f"gs://prism-sessions/{expected_path}"


@pytest.mark.asyncio
async def test_write_json_with_extension_and_uppercase_uuid(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = True
    mock_bucket.blob.return_value = blob_mock

    data = {"readiness": "high"}
    result = await storage.write_json(
        VALID_UPPER_SESSION_ID,
        "investor_readiness.json",
        data,
    )

    expected_path = f"{VALID_SESSION_ID}/investor_readiness.json"
    mock_bucket.blob.assert_called_once_with(expected_path)
    assert result == f"gs://prism-sessions/{expected_path}"


@pytest.mark.asyncio
async def test_write_json_confirmation_failure(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = False
    mock_bucket.blob.return_value = blob_mock

    with pytest.raises(StorageError) as exc_info:
        await storage.write_json(VALID_SESSION_ID, "heatmap", {"risk": "low"})

    assert exc_info.value.detail == "Write confirmation failed"


@pytest.mark.asyncio
async def test_read_json_success(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = True
    data = {"status": "ok", "items": [1, 2, 3]}
    blob_mock.download_as_text.return_value = json.dumps(data)
    mock_bucket.blob.return_value = blob_mock

    result = await storage.read_json(VALID_SESSION_ID, "agent_vc")

    expected_path = f"{VALID_SESSION_ID}/agent_vc.json"
    mock_bucket.blob.assert_called_once_with(expected_path)
    blob_mock.exists.assert_called_once()
    blob_mock.download_as_text.assert_called_once()
    assert result == data


@pytest.mark.asyncio
async def test_read_json_with_extension(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = True
    data = {"cto": "verified"}
    blob_mock.download_as_text.return_value = json.dumps(data)
    mock_bucket.blob.return_value = blob_mock

    result = await storage.read_json(VALID_SESSION_ID, "agent_cto.json")

    expected_path = f"{VALID_SESSION_ID}/agent_cto.json"
    mock_bucket.blob.assert_called_once_with(expected_path)
    assert result == data


@pytest.mark.asyncio
async def test_read_json_missing_blob_returns_none(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = False
    mock_bucket.blob.return_value = blob_mock

    result = await storage.read_json(VALID_SESSION_ID, "agent_lean")

    assert result is None
    blob_mock.download_as_text.assert_not_called()


@pytest.mark.asyncio
async def test_write_pdf_success(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = True
    mock_bucket.blob.return_value = blob_mock

    pdf_bytes = b"%PDF-1.4 test binary data"
    result = await storage.write_pdf(
        VALID_SESSION_ID,
        "ignored_filename.pdf",
        pdf_bytes,
        view="investor",
    )

    expected_path = f"{VALID_SESSION_ID}/output_investor.pdf"
    mock_bucket.blob.assert_called_once_with(expected_path)
    blob_mock.upload_from_string.assert_called_once_with(
        pdf_bytes,
        content_type="application/pdf",
    )
    blob_mock.exists.assert_called_once()
    assert result == f"gs://prism-sessions/{expected_path}"


@pytest.mark.asyncio
async def test_write_pdf_views(mock_bucket):
    for view in ["investor", "technical", "regulatory"]:
        blob_mock = MagicMock()
        blob_mock.exists.return_value = True
        mock_bucket.blob.return_value = blob_mock

        result = await storage.write_pdf(VALID_SESSION_ID, "", b"bytes", view=view)
        assert result == f"gs://prism-sessions/{VALID_SESSION_ID}/output_{view}.pdf"


@pytest.mark.asyncio
async def test_write_pdf_invalid_view(mock_bucket):
    with pytest.raises(StorageError) as exc_info:
        await storage.write_pdf(VALID_SESSION_ID, "", b"bytes", view="executive")

    assert exc_info.value.detail == "Invalid view"


@pytest.mark.asyncio
async def test_write_pdf_confirmation_failure(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.return_value = False
    mock_bucket.blob.return_value = blob_mock

    with pytest.raises(StorageError) as exc_info:
        await storage.write_pdf(VALID_SESSION_ID, "", b"bytes", view="technical")

    assert exc_info.value.detail == "Write confirmation failed"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_id",
    [
        "invalid-uuid-string",
        "12345",
        "",
        "../etc/passwd",
        "../../12345678-1234-5678-1234-567812345678",
        "12345678-1234-5678-1234-567812345678/extra",
    ],
)
async def test_invalid_session_id_rejected(mock_bucket, invalid_id):
    with pytest.raises(StorageError) as exc_info:
        await storage.write_json(invalid_id, "agent_vc", {"key": "val"})
    assert exc_info.value.detail == "Invalid session ID"

    with pytest.raises(StorageError) as exc_info:
        await storage.read_json(invalid_id, "agent_vc")
    assert exc_info.value.detail == "Invalid session ID"

    with pytest.raises(StorageError) as exc_info:
        await storage.write_pdf(invalid_id, "", b"bytes", view="investor")
    assert exc_info.value.detail == "Invalid session ID"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unknown_filename",
    [
        "unknown_file",
        "passwords",
        "agent_random",
        "agent_vc_extra",
        "merged_brd_v2",
        "intake_package.txt",
    ],
)
async def test_unknown_filename_rejected(mock_bucket, unknown_filename):
    with pytest.raises(StorageError) as exc_info:
        await storage.write_json(VALID_SESSION_ID, unknown_filename, {"key": "val"})
    assert exc_info.value.detail == "Invalid filename"

    with pytest.raises(StorageError) as exc_info:
        await storage.read_json(VALID_SESSION_ID, unknown_filename)
    assert exc_info.value.detail == "Invalid filename"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path_traversal",
    [
        "../intake_package",
        "../../agent_vc",
        "/agent_cto",
        "..\\agent_ux",
        "agent_lean/../agent_lean",
        "intake_package.json/../secret",
    ],
)
async def test_path_traversal_filenames_rejected(mock_bucket, path_traversal):
    with pytest.raises(StorageError) as exc_info:
        await storage.write_json(VALID_SESSION_ID, path_traversal, {"key": "val"})
    assert exc_info.value.detail == "Invalid filename"

    with pytest.raises(StorageError) as exc_info:
        await storage.read_json(VALID_SESSION_ID, path_traversal)
    assert exc_info.value.detail == "Invalid filename"


@pytest.mark.asyncio
async def test_unexpected_gcs_exception_on_write(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.upload_from_string.side_effect = RuntimeError("GCS connection timeout")
    mock_bucket.blob.return_value = blob_mock

    with pytest.raises(StorageError) as exc_info:
        await storage.write_json(VALID_SESSION_ID, "score_matrix", {})

    assert exc_info.value.message == "Storage operation failed"
    assert exc_info.value.detail == "RuntimeError"


@pytest.mark.asyncio
async def test_unexpected_gcs_exception_on_read(mock_bucket):
    blob_mock = MagicMock()
    blob_mock.exists.side_effect = ConnectionResetError("Socket reset")
    mock_bucket.blob.return_value = blob_mock

    with pytest.raises(StorageError) as exc_info:
        await storage.read_json(VALID_SESSION_ID, "score_matrix")

    assert exc_info.value.message == "Storage operation failed"
    assert exc_info.value.detail == "ConnectionResetError"
