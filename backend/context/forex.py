"""backend/context/forex.py — Open foreign exchange and currency valuation harvester.

Uses open.er-api.com. 100% free, zero API keys required.
"""

import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = 4.0
_BASE_URL = "https://open.er-api.com/v6/latest/USD"

_REGION_CURRENCIES: dict[str, dict[str, str]] = {
    "IN": {"currency": "INR", "name": "Indian Rupee", "symbol": "₹"},
    "US": {"currency": "USD", "name": "US Dollar", "symbol": "$"},
    "GB": {"currency": "GBP", "name": "British Pound", "symbol": "£"},
    "SG": {"currency": "SGD", "name": "Singapore Dollar", "symbol": "S$"},
    "AE": {"currency": "AED", "name": "UAE Dirham", "symbol": "د.إ"},
    "DE": {"currency": "EUR", "name": "Euro", "symbol": "€"},
    "AU": {"currency": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    "CA": {"currency": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
    "JP": {"currency": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    "NG": {"currency": "NGN", "name": "Nigerian Naira", "symbol": "₦"},
    "BR": {"currency": "BRL", "name": "Brazilian Real", "symbol": "R$"},
}

_FALLBACK_RATES: dict[str, float] = {
    "INR": 86.5,
    "USD": 1.0,
    "GBP": 0.78,
    "SGD": 1.34,
    "AED": 3.67,
    "EUR": 0.92,
    "AUD": 1.52,
    "CAD": 1.38,
    "JPY": 152.0,
    "NGN": 1500.0,
    "BRL": 5.4,
}


async def fetch_forex_data(region: str) -> dict[str, Any]:
    """Fetch live currency valuation and exchange rate against USD.

    100% free, zero keys required. Always returns a structured dict. Never raises.
    """
    clean_region = region.strip().upper() if isinstance(region, str) else "IN"
    curr_info = _REGION_CURRENCIES.get(clean_region, _REGION_CURRENCIES["IN"])
    currency_code = curr_info["currency"]

    rate = _FALLBACK_RATES.get(currency_code, 1.0)
    source = "cached_baseline"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            res = await client.get(_BASE_URL)
            if res.is_success:
                data = res.json()
                rates = data.get("rates", {})
                if currency_code in rates:
                    rate = float(rates[currency_code])
                    source = "open_exchange_rates_api"
    except Exception as e:
        logger.warning("forex_fetch_warning: region=%s, error=%s", region, e)

    return {
        "base_currency": "USD",
        "local_currency": currency_code,
        "currency_name": curr_info["name"],
        "currency_symbol": curr_info["symbol"],
        "exchange_rate_per_usd": round(rate, 2),
        "forex_volatility_risk": "Low" if currency_code in ["USD", "EUR", "GBP", "SGD", "AED"] else "Moderate",
        "data_source": source,
    }
