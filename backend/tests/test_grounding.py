"""backend/tests/test_grounding.py — Unit tests for Gemini Grounding cultural client."""

from unittest.mock import MagicMock
import pytest
from backend.context.grounding import fetch_gemini_grounding


@pytest.mark.asyncio
async def test_grounding_model_success(monkeypatch):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "In India, UPI and localized mobile UX drive hypergrowth."
    mock_model.generate_content.return_value = mock_response

    monkeypatch.setattr("backend.context.grounding.get_flash_model", lambda: mock_model)
    monkeypatch.setattr("backend.context.grounding.init_vertex_ai", lambda: None)

    result = await fetch_gemini_grounding("India", "Fintech")

    assert "UPI and localized mobile UX" in result
    mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_grounding_failure_uses_fallback(monkeypatch):
    def raise_error():
        raise RuntimeError("Vertex AI unavailable")

    monkeypatch.setattr("backend.context.grounding.get_flash_model", raise_error)
    monkeypatch.setattr("backend.context.grounding.init_vertex_ai", lambda: None)

    result = await fetch_gemini_grounding("India", "Fintech")

    assert "UPI payment integrations" in result


@pytest.mark.asyncio
async def test_grounding_us_fallback(monkeypatch):
    def raise_error():
        raise RuntimeError("ADC not configured")

    monkeypatch.setattr("backend.context.grounding.get_flash_model", raise_error)
    monkeypatch.setattr("backend.context.grounding.init_vertex_ai", lambda: None)

    result = await fetch_gemini_grounding("United States", "SaaS")

    assert "United States" in result or "SaaS" in result or "self-serve onboarding" in result


@pytest.mark.asyncio
async def test_invalid_input_returns_default():
    result = await fetch_gemini_grounding("", "")
    assert isinstance(result, str)
    assert len(result) > 20
