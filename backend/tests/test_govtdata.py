"""backend/tests/test_govtdata.py — Unit tests for Government open data client."""

import pytest
from backend.context.govtdata import fetch_govtdata


@pytest.mark.asyncio
async def test_india_fintech_regulatory_flags():
    result = await fetch_govtdata("India", "Fintech")

    assert result["source"] == "govt_open_data"
    assert len(result["regulatory_flags"]) >= 3
    assert any("RBI" in flag for flag in result["regulatory_flags"])
    assert any("DPDP" in flag for flag in result["regulatory_flags"])
    assert result["compliance_authority"] == "Reserve Bank of India (RBI)"
    assert len(result["schemes"]) >= 1


@pytest.mark.asyncio
async def test_india_healthtech():
    result = await fetch_govtdata("IN", "HealthTech")

    assert any("ABDM" in flag for flag in result["regulatory_flags"])
    assert any("Telemedicine" in flag for flag in result["regulatory_flags"])


@pytest.mark.asyncio
async def test_us_fintech():
    result = await fetch_govtdata("US", "Fintech")

    assert any("CFPB" in flag for flag in result["regulatory_flags"])
    assert any("PCI-DSS" in flag for flag in result["regulatory_flags"])


@pytest.mark.asyncio
async def test_unsupported_region_returns_empty_flags():
    result = await fetch_govtdata("Atlantis", "Fintech")

    assert result["source"] == "govt_open_data"
    assert result["regulatory_flags"] == []
    assert result["schemes"] == []
    assert result["compliance_authority"] is None


@pytest.mark.asyncio
async def test_invalid_types_return_empty_flags():
    result = await fetch_govtdata(None, 123)  # type: ignore

    assert result["regulatory_flags"] == []
    assert result["schemes"] == []
