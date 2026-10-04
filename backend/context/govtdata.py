"""backend/context/govtdata.py — Government open data and regulatory compliance client."""

from typing import Any

_GOVT_REGULATORY_DATA: dict[str, dict[str, dict[str, Any]]] = {
    "in": {
        "fintech": {
            "regulatory_flags": [
                "RBI Digital Lending Guidelines (2022) compliance required",
                "Digital Personal Data Protection (DPDP) Act 2023 adherence",
                "Mandatory CERT-In cybersecurity reporting within 6 hours",
                "Prevention of Money Laundering Act (PMLA) KYC norms",
            ],
            "schemes": [
                "Startup India Seed Fund Scheme (SISFS)",
                "RBI Regulatory Sandbox for FinTech",
                "Pradhan Mantri Jan Dhan Yojana integration APIs",
            ],
            "compliance_authority": "Reserve Bank of India (RBI)",
        },
        "healthtech": {
            "regulatory_flags": [
                "Ayushman Bharat Digital Mission (ABDM) health data standards",
                "DPDP Act 2023 sensitive personal data protection",
                "Telemedicine Practice Guidelines (2020)",
                "CDSCO Software as a Medical Device (SaMD) registration",
            ],
            "schemes": [
                "National Digital Health Mission Sandbox",
                "Ayushman Bharat PM-JAY integration",
            ],
            "compliance_authority": "National Health Authority (NHA) & CDSCO",
        },
        "agritech": {
            "regulatory_flags": [
                "AgriStack Digital Agriculture Mission compliance",
                "Farmer data privacy and consent protocol adherence",
                "Essential Commodities Act regulatory norms",
            ],
            "schemes": [
                "Agriculture Infrastructure Fund (AIF)",
                "PM Kisan Samman Nidhi open data integration",
                "Formation and Promotion of 10,000 FPOs scheme",
            ],
            "compliance_authority": "Ministry of Agriculture & Farmers Welfare",
        },
        "edtech": {
            "regulatory_flags": [
                "National Education Policy (NEP 2020) online curriculum standards",
                "UGC / AICTE guidelines for online and distance learning",
                "Consumer Protection (E-Commerce) Rules for subscriptions",
            ],
            "schemes": [
                "DIKSHA / SWAYAM digital infrastructure integration",
                "Skill India Mission startup support",
            ],
            "compliance_authority": "Ministry of Education & AICTE",
        },
        "default": {
            "regulatory_flags": [
                "Digital Personal Data Protection (DPDP) Act 2023 compliance",
                "Ministry of Corporate Affairs (MCA) incorporation filings",
                "Standard GST compliance (Central and State)",
            ],
            "schemes": ["Startup India Recognition & Tax Exemptions (Section 80-IAC)"],
            "compliance_authority": "Ministry of Corporate Affairs / DPIIT",
        },
    },
    "us": {
        "fintech": {
            "regulatory_flags": [
                "CFPB Consumer Financial Protection regulations",
                "FinCEN Bank Secrecy Act / Anti-Money Laundering rules",
                "SEC / FINRA securities compliance if tokenized/invested",
                "PCI-DSS payment security standards",
            ],
            "schemes": ["SBA Small Business Innovation Research (SBIR) program"],
            "compliance_authority": "CFPB, SEC, FinCEN",
        },
        "healthtech": {
            "regulatory_flags": [
                "HIPAA Privacy and Security Rules compliance",
                "FDA Digital Health Center of Excellence regulatory framework",
                "HITECH Act breach notification guidelines",
            ],
            "schemes": ["NIH Small Business Health Tech grants"],
            "compliance_authority": "HHS Office for Civil Rights & FDA",
        },
        "default": {
            "regulatory_flags": [
                "FTC Consumer Privacy guidelines",
                "State-level data protection (CCPA/CPRA)",
            ],
            "schemes": ["US Small Business Administration (SBA) Loan Programs"],
            "compliance_authority": "Federal Trade Commission (FTC)",
        },
    },
    "ng": {
        "default": {
            "regulatory_flags": [
                "NDPR — Nigeria Data Protection Regulation applies",
                "CBN licensing required for fintech and payments",
                "CAC registration required for all businesses",
            ],
            "schemes": ["Nigeria Startup Act tax reliefs and grants"],
            "compliance_authority": "Central Bank of Nigeria (CBN) & NITDA",
        }
    },
    "de": {
        "default": {
            "regulatory_flags": [
                "GDPR strictly enforced — highest fines in EU",
                "BaFin licensing required for all financial products",
                "BSI cybersecurity standards for critical infrastructure",
            ],
            "schemes": ["EXIST Business Start-up Grant by Federal Ministry for Economic Affairs"],
            "compliance_authority": "BaFin & Federal Commissioner for Data Protection",
        }
    },
    "au": {
        "default": {
            "regulatory_flags": [
                "Privacy Act 1988 + Australian Privacy Principles",
                "ASIC licensing for financial services",
                "TGA approval required for health-related products",
            ],
            "schemes": ["R&D Tax Incentive and Accelerating Commercialisation grants"],
            "compliance_authority": "ASIC & OAIC",
        }
    },
    "ae": {
        "default": {
            "regulatory_flags": [
                "DIFC or ADGM free zone registration for fintech",
                "UAE PDPL — Personal Data Protection Law 2022",
                "No corporate tax for most qualifying free zone entities",
            ],
            "schemes": ["Hub71 Abu Dhabi / Dubai Future Accelerators incentives"],
            "compliance_authority": "DFSA / FSRA / UAE Central Bank",
        }
    },
    "sg": {
        "default": {
            "regulatory_flags": [
                "PDPA — Personal Data Protection Act compliance",
                "MAS Payment Services Act licensing for digital payments",
                "ACRA mandatory statutory filings",
            ],
            "schemes": ["Startup SG Founder and Tech.Pass initiative"],
            "compliance_authority": "Monetary Authority of Singapore (MAS) & PDPC",
        }
    },
    "gb": {
        "default": {
            "regulatory_flags": [
                "UK GDPR and Data Protection Act 2018 compliance",
                "FCA authorization for financial activities",
                "Companies House statutory reporting",
            ],
            "schemes": ["SEIS/EIS tax relief schemes for investors"],
            "compliance_authority": "Financial Conduct Authority (FCA) & ICO",
        }
    },
}

_REGION_ALIASES: dict[str, str] = {
    "in": "in",
    "india": "in",
    "us": "us",
    "united states": "us",
    "usa": "us",
    "ng": "ng",
    "nigeria": "ng",
    "de": "de",
    "germany": "de",
    "deutschland": "de",
    "au": "au",
    "australia": "au",
    "ae": "ae",
    "uae": "ae",
    "united arab emirates": "ae",
    "sg": "sg",
    "singapore": "sg",
    "gb": "gb",
    "uk": "gb",
    "united kingdom": "gb",
}


async def fetch_govtdata(region: str, industry: str) -> dict[str, Any]:
    if not isinstance(region, str) or not isinstance(industry, str):
        return {"regulatory_flags": [], "schemes": [], "compliance_authority": None, "source": "govt_open_data"}

    clean_region = region.strip().lower()
    clean_industry = industry.strip().lower()

    canonical_region = _REGION_ALIASES.get(clean_region)
    if not canonical_region:
        return {
            "regulatory_flags": [],
            "schemes": [],
            "compliance_authority": None,
            "source": "govt_open_data",
        }

    region_data = _GOVT_REGULATORY_DATA.get(canonical_region, {})
    matched_industry_data = region_data.get(clean_industry)
    if not matched_industry_data:
        for ind_key, ind_val in region_data.items():
            if ind_key != "default" and (ind_key in clean_industry or clean_industry in ind_key):
                matched_industry_data = ind_val
                break

    if not matched_industry_data:
        matched_industry_data = region_data.get("default", {"regulatory_flags": [], "schemes": []})

    return {
        "regulatory_flags": list(matched_industry_data.get("regulatory_flags", [])),
        "schemes": list(matched_industry_data.get("schemes", [])),
        "compliance_authority": matched_industry_data.get("compliance_authority"),
        "source": "govt_open_data",
    }
