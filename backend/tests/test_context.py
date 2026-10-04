"""backend/tests/test_context.py — Unit tests for context layer pure logic, cache, and fallbacks."""

import asyncio
import os
import pytest

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.config import settings
else:
    try:
        from backend.config import settings
    except ImportError:
        from config import settings

from context.crunchbase import _get_fallback, fetch_crunchbase
from context.govtdata import fetch_govtdata
from context.grounding import fetch_gemini_grounding
from context.harvester import harvest_context
from context.newsapi import _CACHE, _cache_key, _get_cached, _set_cache, fetch_news
from models.context import NewsItem
from models.intake import IntakePackage


class TestNewsAPICache:
    def test_cache_key_is_md5(self) -> None:
        key = _cache_key("IN", "fintech")
        assert len(key) == 32
        assert key.isalnum()

    def test_cache_key_case_insensitive(self) -> None:
        assert _cache_key("IN", "fintech") == _cache_key("in", "FINTECH")

    def test_set_and_get_cache(self) -> None:
        items = [NewsItem(title="Test Article", source="Test Source")]
        _set_cache("SG", "edtech", items)
        cached = _get_cached("SG", "edtech")
        assert cached is not None
        assert len(cached) == 1
        assert cached[0].title == "Test Article"

    def test_cache_miss_returns_none(self) -> None:
        result = _get_cached("ZZ", "nonexistent-industry-xyz")
        assert result is None

    def test_no_api_key_returns_empty(self) -> None:
        orig_key = settings.NEWSAPI_KEY
        settings.NEWSAPI_KEY = ""
        try:
            result = asyncio.run(fetch_news("US", "saas"))
            assert result == []
        finally:
            settings.NEWSAPI_KEY = orig_key


class TestCrunchbaseFallback:
    def test_fintech_fallback_has_rounds(self) -> None:
        f = _get_fallback("fintech startup")
        assert f["data_source"] == "static_fallback"
        assert len(f["recent_rounds"]) > 0

    def test_unknown_industry_returns_default(self) -> None:
        f = _get_fallback("quantum computing for bees")
        assert f["data_source"] == "static_fallback"
        assert f["recent_rounds"] == []

    def test_no_key_returns_fallback(self) -> None:
        orig_key = settings.CRUNCHBASE_KEY
        settings.CRUNCHBASE_KEY = ""
        try:
            result = asyncio.run(fetch_crunchbase("edtech"))
            assert result["data_source"] == "static_fallback"
        finally:
            settings.CRUNCHBASE_KEY = orig_key


class TestGovtData:
    def test_india_fintech_has_rbi_flag(self) -> None:
        result = asyncio.run(fetch_govtdata("IN", "fintech"))
        assert result["data_source"] == "static_regulatory_map"
        flags_str = str(result["regulatory_flags"])
        assert "RBI" in flags_str or "DPDP" in flags_str

    def test_us_healthtech_has_hipaa(self) -> None:
        result = asyncio.run(fetch_govtdata("US", "healthtech"))
        flags_str = str(result["regulatory_flags"])
        assert "HIPAA" in flags_str

    def test_unknown_region_returns_default_flags(self) -> None:
        result = asyncio.run(fetch_govtdata("ZZ", "unknown"))
        assert result["data_source"] == "static_regulatory_map"
        assert len(result["regulatory_flags"]) > 0

    def test_empty_inputs_no_crash(self) -> None:
        result = asyncio.run(fetch_govtdata("", ""))
        assert isinstance(result["regulatory_flags"], list)

    def test_returns_compliance_notes(self) -> None:
        result = asyncio.run(fetch_govtdata("GB", "fintech"))
        assert "compliance_notes" in result
        assert len(result["compliance_notes"]) > 10


class TestGrounding:
    def test_empty_region_returns_empty_string(self) -> None:
        result = asyncio.run(fetch_gemini_grounding("", "fintech"))
        assert result == ""

    def test_empty_industry_returns_empty_string(self) -> None:
        result = asyncio.run(fetch_gemini_grounding("IN", ""))
        assert result == ""


class TestHarvester:
    def test_returns_valid_context_package_on_all_failure(self, sample_intake: IntakePackage) -> None:
        result = asyncio.run(harvest_context(sample_intake))
        assert result.session_id == sample_intake.session_id
        assert isinstance(result.failed_sources, list)
        assert isinstance(result.regulatory_flags, list)

    def test_regulatory_flags_populated_from_govtdata(self, sample_intake: IntakePackage) -> None:
        result = asyncio.run(harvest_context(sample_intake))
        # govtdata never fails — so regulatory_flags must always be populated
        assert len(result.regulatory_flags) > 0

    def test_failed_sources_is_list(self, sample_intake: IntakePackage) -> None:
        result = asyncio.run(harvest_context(sample_intake))
        assert isinstance(result.failed_sources, list)
