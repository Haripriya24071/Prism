"""backend/tests/test_api.py — Integration tests for FastAPI HTTP endpoints."""

import os
from typing import Any
import pytest
from fastapi.testclient import TestClient

os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["ENV"] = "development"


class TestHealthEndpoint:
    def test_health_returns_200(self, test_client: TestClient) -> None:
        r = test_client.get("/health")
        assert r.status_code == 200

    def test_health_response_shape(self, test_client: TestClient) -> None:
        r = test_client.get("/health")
        data = r.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "ok"


class TestSessionEndpoints:
    def test_create_session_returns_201(self, test_client: TestClient) -> None:
        r = test_client.post("/intake/session")
        assert r.status_code == 201

    def test_create_session_returns_session_id(self, test_client: TestClient) -> None:
        r = test_client.post("/intake/session")
        data = r.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 8

    def test_get_session_valid_id(self, test_client: TestClient) -> None:
        sid = test_client.post("/intake/session").json()["session_id"]
        r = test_client.get(f"/intake/session/{sid}")
        assert r.status_code == 200
        assert r.json()["session_id"] == sid

    def test_get_session_invalid_id_returns_404(self, test_client: TestClient) -> None:
        r = test_client.get("/intake/session/nonexistent-bad-id")
        assert r.status_code == 404

    def test_404_response_has_error_key(self, test_client: TestClient) -> None:
        r = test_client.get("/intake/session/nonexistent-bad-id")
        data = r.json()
        assert "error" in data
        assert "message" in data
        assert "SessionNotFoundError" in data["error"]


class TestChatEndpoint:
    def test_chat_bad_session_returns_404(self, test_client: TestClient) -> None:
        r = test_client.post(
            "/intake/chat",
            json={
                "session_id": "bad-session-id",
                "message": "hello",
                "turn_number": 0,
            },
        )
        assert r.status_code == 404

    def test_chat_invalid_payload_returns_422(self, test_client: TestClient) -> None:
        r = test_client.post("/intake/chat", json={"invalid": "payload"})
        assert r.status_code == 422

    def test_chat_session_id_too_short_returns_422(self, test_client: TestClient) -> None:
        r = test_client.post(
            "/intake/chat",
            json={
                "session_id": "abc",
                "message": "hello",
                "turn_number": 0,
            },
        )
        assert r.status_code == 422


class TestGenerateEndpoints:
    def test_generate_bad_session_returns_404(self, test_client: TestClient) -> None:
        r = test_client.post("/generate?session_id=nonexistent-bad-id")
        assert r.status_code == 404

    def test_generate_no_intake_returns_error(self, test_client: TestClient) -> None:
        sid = test_client.post("/intake/session").json()["session_id"]
        r = test_client.post(f"/generate?session_id={sid}")
        # No intake_package yet — should return 422 IntakeError
        assert r.status_code in (422, 500)

    def test_generate_stream_invalid_session(self, test_client: TestClient) -> None:
        r = test_client.get("/generate/stream/nonexistent-bad-id")
        assert r.status_code == 404


class TestBRDEndpoints:
    def test_brd_not_ready_returns_200_with_null_brd(self, test_client: TestClient) -> None:
        sid = test_client.post("/intake/session").json()["session_id"]
        r = test_client.get(f"/brd/{sid}")
        assert r.status_code == 200
        assert r.json()["brd"] is None

    def test_brd_missing_session_returns_404(self, test_client: TestClient) -> None:
        r = test_client.get("/brd/nonexistent-bad-id")
        assert r.status_code == 404

    def test_pdf_invalid_view_returns_400(self, test_client: TestClient) -> None:
        sid = test_client.post("/intake/session").json()["session_id"]
        r = test_client.get(f"/brd/{sid}/pdf?view=invalid")
        assert r.status_code == 400

    def test_pdf_valid_view_returns_200(self, test_client: TestClient) -> None:
        sid = test_client.post("/intake/session").json()["session_id"]
        for view in ["investor", "technical", "regulatory"]:
            r = test_client.get(f"/brd/{sid}/pdf?view={view}")
            assert r.status_code == 200
            data = r.json()
            assert "view" in data
            assert "available" in data

    def test_pdf_missing_session_returns_404(self, test_client: TestClient) -> None:
        r = test_client.get("/brd/nonexistent-bad-id/pdf?view=investor")
        assert r.status_code == 404

    def test_pdf_streams_when_brd_complete(self, test_client: TestClient) -> None:
        from backend.session_store import update_session
        sid = test_client.post("/intake/session").json()["session_id"]
        mock_brd = {
            "session_id": sid,
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": "A high-growth enterprise platform.",
                    "lineage": {"source_agent": "vc", "confidence": 0.9, "data_citation": "Source"},
                }
            ],
            "investor_readiness_score": 85,
        }
        update_session(sid, brd=mock_brd, status="complete", score=85)
        for view in ["investor", "technical", "regulatory"]:
            r = test_client.get(f"/brd/{sid}/pdf?view={view}")
            assert r.status_code == 200
            assert r.headers["content-type"] == "application/pdf"
            assert f'attachment; filename="prism-brd-{view}.pdf"' in r.headers["content-disposition"]
            assert r.content.startswith(b"%PDF")
