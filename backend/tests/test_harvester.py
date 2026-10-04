"""backend/tests/test_harvester.py — Unit tests for context harvester orchestrator."""

import pytest
from backend.context import harvester
from backend.models.context import ContextPackage, MarketData, NewsItem
from backend.models.intake import IntakeExtraction, IntakePackage


def _create_sample_intake() -> IntakePackage:
    return IntakePackage(
        session_id="12345678-1234-5678-1234-567812345678",
        extraction=IntakeExtraction(
            raw_idea="B2B AI invoice management",
            region="IN",
            industry="Fintech",
            stage="idea",
        ),
    )


@pytest.mark.asyncio
async def test_harvest_context_all_succeed(monkeypatch):
    async def mock_news(region, industry):
        return [
            NewsItem(
                title="Fintech Surge",
                source="Economic Times",
                url="https://economictimes.com/fintech",
            )
        ]

    async def mock_worldbank(region):
        return MarketData(gdp_per_capita_usd=2500.0, inflation_rate_pct=5.0, source_year=2023)

    async def mock_crunchbase(industry):
        return {"source": "crunchbase_static_fallback", "competitors": [{"name": "Razorpay"}]}

    async def mock_govt(region, industry):
        return {"regulatory_flags": ["RBI Digital Lending Guidelines"], "source": "govt_open_data"}

    async def mock_grounding(region, industry):
        return "India relies heavily on UPI and mobile banking."

    async def mock_gdelt(region, industry):
        return {"political_events": [{"title": "RBI policy update", "url": "https://rbi.org.in"}]}

    async def mock_alphavantage(region, key):
        return {"market_mood": "bullish", "market_sentiment_score": 0.22}

    monkeypatch.setattr(harvester, "fetch_news", mock_news)
    monkeypatch.setattr(harvester, "fetch_worldbank", mock_worldbank)
    monkeypatch.setattr(harvester, "fetch_crunchbase", mock_crunchbase)
    monkeypatch.setattr(harvester, "fetch_govtdata", mock_govt)
    monkeypatch.setattr(harvester, "fetch_gemini_grounding", mock_grounding)
    monkeypatch.setattr(harvester, "fetch_political_context", mock_gdelt)
    monkeypatch.setattr(harvester, "fetch_market_sentiment", mock_alphavantage)

    intake = _create_sample_intake()
    pkg = await harvester.harvest_context(intake)

    assert isinstance(pkg, ContextPackage)
    assert pkg.session_id == intake.session_id
    assert pkg.region == "IN"
    assert pkg.industry == "Fintech"
    assert len(pkg.news_items) == 1
    assert pkg.market_data is not None
    assert pkg.market_data.gdp_per_capita_usd == 2500.0
    assert pkg.crunchbase_data.get("competitors")[0]["name"] == "Razorpay"
    assert "RBI Digital Lending Guidelines" in pkg.regulatory_flags
    assert "UPI" in str(pkg.cultural_context)
    assert "https://economictimes.com/fintech" in pkg.source_urls
    assert "https://rbi.org.in" in pkg.source_urls
    assert pkg.market_sentiment.get("market_mood") == "bullish"
    assert pkg.failed_sources == []


@pytest.mark.asyncio
async def test_harvest_context_partial_failure_resilience(monkeypatch):
    async def mock_news(region, industry):
        raise RuntimeError("NewsAPI service unavailable")

    async def mock_worldbank(region):
        return MarketData(gdp_per_capita_usd=2500.0, source_year=2023)

    async def mock_crunchbase(industry):
        raise TimeoutError("Crunchbase timeout")

    async def mock_govt(region, industry):
        return {"regulatory_flags": ["RBI Norms"], "source": "govt_open_data"}

    async def mock_grounding(region, industry):
        return "Cultural summary."

    async def mock_gdelt(region, industry):
        raise TimeoutError("GDELT timeout")

    async def mock_alphavantage(region, key):
        return {}

    monkeypatch.setattr(harvester, "fetch_news", mock_news)
    monkeypatch.setattr(harvester, "fetch_worldbank", mock_worldbank)
    monkeypatch.setattr(harvester, "fetch_crunchbase", mock_crunchbase)
    monkeypatch.setattr(harvester, "fetch_govtdata", mock_govt)
    monkeypatch.setattr(harvester, "fetch_gemini_grounding", mock_grounding)
    monkeypatch.setattr(harvester, "fetch_political_context", mock_gdelt)
    monkeypatch.setattr(harvester, "fetch_market_sentiment", mock_alphavantage)

    intake = _create_sample_intake()
    pkg = await harvester.harvest_context(intake)

    assert isinstance(pkg, ContextPackage)
    assert "newsapi" in pkg.failed_sources
    assert "crunchbase" in pkg.failed_sources
    assert "gdelt" in pkg.failed_sources
    assert pkg.news_items == []
    assert pkg.market_data is not None
    assert pkg.market_data.gdp_per_capita_usd == 2500.0
    assert pkg.regulatory_flags == ["RBI Norms"]
    assert pkg.cultural_context == "Cultural summary."
