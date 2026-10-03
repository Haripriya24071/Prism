"""backend/context/govtdata.py — Government open data integration client."""

from typing import Any
import structlog

logger = structlog.get_logger()

# Regional regulatory flag mappings — structured static data
# Labelled as static so agents cite it correctly
_REGULATORY_MAP: dict[str, dict[str, Any]] = {
    "IN": {
        "regulatory_flags": [
            "DPDP Act 2023 — Digital Personal Data Protection Act applies to all user data",
            "RBI licensing required for payment and lending products",
            "SEBI registration for investment or wealth management products",
            "GST compliance mandatory for B2B SaaS above ₹20L turnover",
            "Startup India DPIIT registration available for tax exemptions",
        ],
        "compliance_notes": "India has sector-specific regulators. Fintech requires RBI sandbox approval. Healthtech requires CDSCO compliance.",
        "data_source": "static_regulatory_map",
    },
    "US": {
        "regulatory_flags": [
            "CCPA compliance required for California users",
            "SOC 2 Type II expected by enterprise customers",
            "HIPAA compliance mandatory for any health data",
            "SEC/FINRA registration for financial products",
            "ADA compliance required for accessibility",
        ],
        "compliance_notes": "US has state-level data laws. Delaware C-Corp preferred for VC funding. GDPR applies if serving EU users.",
        "data_source": "static_regulatory_map",
    },
    "GB": {
        "regulatory_flags": [
            "UK GDPR and Data Protection Act 2018 — post-Brexit version",
            "FCA authorisation required for financial services",
            "ICO registration required for data processing",
            "CMA scrutiny for any market-dominant product",
        ],
        "compliance_notes": "UK is post-Brexit — separate compliance from EU required. FCA sandbox available for fintech.",
        "data_source": "static_regulatory_map",
    },
    "SG": {
        "regulatory_flags": [
            "PDPA — Personal Data Protection Act 2012",
            "MAS licensing for payment and financial services",
            "IMDA oversight for digital media and telecom products",
        ],
        "compliance_notes": "Singapore is a common APAC launch hub. MAS fintech sandbox is highly accessible.",
        "data_source": "static_regulatory_map",
    },
}

_DEFAULT_REGULATORY: dict[str, Any] = {
    "regulatory_flags": [
        "GDPR may apply if serving EU residents",
        "Local data residency laws — verify before storing user data",
        "Consumer protection laws — verify refund and cancellation obligations",
    ],
    "compliance_notes": "Region-specific regulatory data not available. Consult a local legal advisor before launch.",
    "data_source": "static_regulatory_map",
}


async def fetch_govtdata(region: str, industry: str) -> dict[str, Any]:
    """Returns regulatory flags and compliance notes for a region + industry."""
    raise NotImplementedError("Phase 5")
