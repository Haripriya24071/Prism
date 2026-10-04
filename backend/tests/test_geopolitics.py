"""backend/tests/test_geopolitics.py — Unit tests for zero-key geopolitics & religion harvester."""

import pytest
from backend.context.geopolitics import fetch_geopolitics_and_religion


@pytest.mark.asyncio
async def test_fetch_geopolitics_india():
    res = await fetch_geopolitics_and_religion("IN")
    assert isinstance(res, dict)
    assert res.get("country") == "India"
    assert "NDA" in res.get("ruling_coalition", "") or "BJP" in res.get("ruling_coalition", "")
    assert "Hinduism" in res.get("religious_demographics", "")
    assert "Diwali" in res.get("religious_demographics", "")
    assert res.get("data_source") == "wikipedia_and_regional_knowledge_base"


@pytest.mark.asyncio
async def test_fetch_geopolitics_us():
    res = await fetch_geopolitics_and_religion("US")
    assert isinstance(res, dict)
    assert res.get("country") == "United States"
    assert "Federal presidential" in res.get("political_system", "")
    assert "Christianity" in res.get("religious_demographics", "")


@pytest.mark.asyncio
async def test_fetch_geopolitics_fallback_for_unknown():
    res = await fetch_geopolitics_and_religion("XYZ_UNKNOWN_REGION")
    assert isinstance(res, dict)
    # Defaults to IN baseline
    assert res.get("country") == "India"
    assert "parliamentary" in res.get("political_system", "").lower()
