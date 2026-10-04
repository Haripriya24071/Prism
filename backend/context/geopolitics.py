"""backend/context/geopolitics.py — Open geopolitical, political party, and religious dynamics harvester.

Uses Wikipedia REST API and verified regional knowledge bases. 100% free, zero API keys required.
"""

import asyncio
import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = 4.0
_HEADERS = {"User-Agent": "PRISM-Business-Intel/1.0 (contact@prism.ai)"}

_COUNTRY_TOPICS: dict[str, dict[str, str]] = {
    "IN": {
        "name": "India",
        "politics_topic": "Politics_of_India",
        "religion_topic": "Religion_in_India",
        "ruling_coalition": "National Democratic Alliance (NDA) led by Bharatiya Janata Party (BJP)",
        "political_system": "Federal parliamentary republic with multi-party democratic system",
        "key_political_factors": (
            "Pro-digitization push (Digital India, India Stack, UPI, ONDC, Make in India); "
            "stringent data localization and DPDP compliance; state vs. federal taxation (GST) harmonization; "
            "active regulatory oversight by RBI, SEBI, and CCI on anti-competitive market concentration."
        ),
        "religious_demographics": (
            "Hinduism (~79.8%), Islam (~14.2%), Christianity (~2.3%), Sikhism (~1.7%), Buddhism (~0.7%), Jainism (~0.4%). "
            "Deep respect for religious sensitivities and vegetarianism/halal dietary norms required in consumer commerce; "
            "massive consumer spending peaks during festive seasons (Diwali, Eid, Dussehra, Ganesh Chaturthi, Durga Puja)."
        ),
    },
    "US": {
        "name": "United States",
        "politics_topic": "Politics_of_the_United_States",
        "religion_topic": "Religion_in_the_United_States",
        "ruling_coalition": "Two-party presidential federal republic (Democratic and Republican parties)",
        "political_system": "Federal presidential constitutional republic",
        "key_political_factors": (
            "Strict antitrust scrutiny from FTC and DOJ; bipartisan focus on supply-chain re-shoring and chip sovereignty; "
            "state-level privacy variance (California CCPA/CPRA, Virginia, Colorado); federal compliance (SEC, HIPAA, OSHA)."
        ),
        "religious_demographics": (
            "Christianity (~65%), Unaffiliated/Secular (~28%), Judaism (~2%), Islam (~1%), others (~4%). "
            "Massive Q4 shopping cycle around Thanksgiving, Black Friday, Cyber Monday, and Christmas."
        ),
    },
    "GB": {
        "name": "United Kingdom",
        "politics_topic": "Politics_of_the_United_Kingdom",
        "religion_topic": "Religion_in_the_United_Kingdom",
        "ruling_coalition": "Labour Party government in parliamentary constitutional monarchy",
        "political_system": "Parliamentary constitutional monarchy with devolution to Scotland, Wales, and Northern Ireland",
        "key_political_factors": (
            "Post-Brexit regulatory regime (UK GDPR, National Security and Investment Act); "
            "pro-fintech regulatory sandbox by Financial Conduct Authority (FCA); strict consumer rights and green energy transition mandates."
        ),
        "religious_demographics": (
            "Christianity (~46%), Non-religious (~37%), Islam (~6.5%), Hinduism (~1.7%). Major holiday sales around Christmas and Boxing Day."
        ),
    },
    "SG": {
        "name": "Singapore",
        "politics_topic": "Politics_of_Singapore",
        "religion_topic": "Religion_in_Singapore",
        "ruling_coalition": "People's Action Party (PAP) in parliamentary republic",
        "political_system": "Unitary dominant-party parliamentary constitutional republic",
        "key_political_factors": (
            "World-leading regulatory predictability, low corruption, and pro-business government grants; "
            "Monetary Authority of Singapore (MAS) progressive fintech frameworks; strict cybersecurity and PDPA compliance."
        ),
        "religious_demographics": (
            "Buddhism (~31%), Christianity (~19%), Islam (~15%), Taoism (~9%), Hinduism (~5%). "
            "Multi-ethnic celebrations: Lunar New Year, Hari Raya, Deepavali, Christmas."
        ),
    },
    "AE": {
        "name": "United Arab Emirates",
        "politics_topic": "Politics_of_the_United_Arab_Emirates",
        "religion_topic": "Religion_in_the_United_Arab_Emirates",
        "ruling_coalition": "Federation of seven hereditary monarchies (Emirates) with federal government",
        "political_system": "Federal elective monarchy with specialized free-trade commercial zones",
        "key_political_factors": (
            "National digital economy strategy, aggressive AI adoption, and zero personal income tax in free zones (DIFC, ADGM); "
            "Virtual Assets Regulatory Authority (VARA) progressive Web3/crypto licensing; strict cybercrime laws."
        ),
        "religious_demographics": (
            "Islam (official religion, ~76%), with large expatriate communities (Christianity, Hinduism, Buddhism). "
            "Ramadan commercial rhythms (night commerce surge) and Eid al-Fitr / Eid al-Adha festive spending peaks."
        ),
    },
    "DE": {
        "name": "Germany",
        "politics_topic": "Politics_of_Germany",
        "religion_topic": "Religion_in_Germany",
        "ruling_coalition": "Multi-party federal parliamentary republic",
        "political_system": "Federal parliamentary democratic republic",
        "key_political_factors": (
            "EU GDPR compliance benchmark, strong works councils (Betriebsrat) and employee privacy protections; "
            "rigorous BaFin financial supervision and environmental sustainability directives."
        ),
        "religious_demographics": (
            "Christianity (~50%), Non-religious (~42%), Islam (~6%). Strong Christmas retail tradition and strict Sunday trading closures."
        ),
    },
}


async def _fetch_wiki_summary(client: httpx.AsyncClient, topic: str) -> str:
    """Fetch 1-paragraph summary from Wikipedia REST API."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    try:
        res = await client.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        if res.is_success:
            data = res.json()
            return data.get("extract", "").strip()
    except Exception:
        pass
    return ""


async def fetch_geopolitics_and_religion(region: str) -> dict[str, Any]:
    """Fetch geopolitical governance, political party stability, and religious/cultural factors.

    100% free, zero keys required. Always returns a rich, structured dictionary. Never raises.
    """
    clean_region = region.strip().upper() if isinstance(region, str) else "IN"
    info = _COUNTRY_TOPICS.get(clean_region, _COUNTRY_TOPICS["IN"])
    country_name = info["name"]

    political_summary = ""
    religious_summary = ""

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            p_task = _fetch_wiki_summary(client, info.get("politics_topic", ""))
            r_task = _fetch_wiki_summary(client, info.get("religion_topic", ""))
            results = await asyncio.gather(p_task, r_task, return_exceptions=True)

            if isinstance(results[0], str) and results[0]:
                political_summary = results[0]
            if isinstance(results[1], str) and results[1]:
                religious_summary = results[1]
    except Exception as e:
        logger.warning("geopolitics_fetch_warning: region=%s, error=%s", region, e)

    return {
        "country": country_name,
        "region_code": clean_region,
        "political_system": info["political_system"],
        "ruling_coalition": info["ruling_coalition"],
        "key_political_factors": info["key_political_factors"],
        "political_summary": political_summary or info["key_political_factors"],
        "religious_demographics": info["religious_demographics"],
        "religious_summary": religious_summary or info["religious_demographics"],
        "data_source": "wikipedia_and_regional_knowledge_base",
    }
