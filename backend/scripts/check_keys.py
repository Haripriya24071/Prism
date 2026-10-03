"""backend/scripts/check_keys.py — External services connectivity and configuration verifier."""

import sys
import time
from typing import Any, Callable, List
import httpx
from google.cloud import bigquery, storage
import vertexai
from vertexai.generative_models import GenerativeModel
from backend.config import settings

TIMEOUT_SECONDS: float = 10.0


def check_newsapi() -> bool:
    name: str = "NewsAPI"
    if not settings.NEWSAPI_KEY or not settings.NEWSAPI_KEY.strip():
        print(f"[FAIL] {name} - key not set")
        return False
    try:
        url: str = "https://newsapi.org/v2/top-headlines"
        headers: dict[str, str] = {"X-Api-Key": settings.NEWSAPI_KEY}
        params: dict[str, Any] = {"country": "in", "pageSize": 1}
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response: httpx.Response = client.get(url, headers=headers, params=params)
        rate_limit: str | None = response.headers.get("x-ratelimit-remaining")
        rate_info: str = f", x-ratelimit-remaining: {rate_limit}" if rate_limit is not None else ""
        if response.is_success:
            print(f"[OK] {name} - Status {response.status_code}{rate_info}")
            return True
        else:
            print(f"[FAIL] {name} - Status {response.status_code}{rate_info}")
            return False
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def check_world_bank() -> bool:
    name: str = "World Bank"
    indicators: list[str] = [
        "NY.GDP.MKTP.CD",
        "FP.CPI.TOTL.ZG",
        "BX.KLT.DINV.WD.GD.ZS",
        "IC.BUS.EASE.XQ",
    ]
    results: list[str] = []
    all_ok: bool = True
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            for ind in indicators:
                url: str = f"https://api.worldbank.org/v2/country/IN/indicator/{ind}"
                params: dict[str, Any] = {"mrnev": 1, "format": "json"}
                resp: httpx.Response = client.get(url, params=params)
                if not resp.is_success:
                    results.append(f"{ind}: HTTP {resp.status_code}")
                    all_ok = False
                    continue
                data: Any = resp.json()
                if isinstance(data, list) and len(data) > 1 and data[1]:
                    entry: dict[str, Any] = data[1][0]
                    val: Any = entry.get("value")
                    year: Any = entry.get("date")
                    if val is not None:
                        results.append(f"{ind}: {year} (non-null)")
                    else:
                        results.append(f"{ind}: {year} (null)")
                else:
                    results.append(f"{ind}: no data")
        status_tag: str = "[OK]" if all_ok else "[FAIL]"
        print(f"{status_tag} {name} - {', '.join(results)}")
        return all_ok
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def check_crunchbase() -> bool:
    name: str = "Crunchbase"
    if not settings.CRUNCHBASE_KEY or not settings.CRUNCHBASE_KEY.strip():
        print(f"[FAIL] {name} - key not set")
        return False
    try:
        url: str = "https://api.crunchbase.com/api/v4/autocompletes"
        headers: dict[str, str] = {"X-cb-user-key": settings.CRUNCHBASE_KEY}
        params: dict[str, Any] = {"query": "google", "limit": 1}
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response: httpx.Response = client.get(url, headers=headers, params=params)
        if response.status_code in (401, 403):
            print(f"[FAIL] {name} - Status {response.status_code} - No usable access - use the static fallback")
            return False
        elif response.is_success:
            print(f"[OK] {name} - Status {response.status_code}")
            return True
        else:
            print(f"[FAIL] {name} - Status {response.status_code}")
            return False
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def check_cloud_storage() -> bool:
    name: str = "Cloud Storage"
    try:
        client: storage.Client = storage.Client(project=settings.GCP_PROJECT_ID)
        bucket: storage.Bucket = client.bucket(settings.GCS_BUCKET_NAME)
        exists: bool = bucket.exists(timeout=TIMEOUT_SECONDS)
        if exists:
            print(f"[OK] {name} - Status 200 (Bucket '{settings.GCS_BUCKET_NAME}' exists)")
            return True
        else:
            print(f"[FAIL] {name} - Bucket '{settings.GCS_BUCKET_NAME}' does not exist")
            return False
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def check_bigquery() -> bool:
    name: str = "BigQuery"
    required_tables: set[str] = {
        "brd_runs",
        "context_harvest_logs",
        "evaluator_scores",
        "divergence_heatmap_data",
    }
    try:
        client: bigquery.Client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        dataset_ref = client.dataset(settings.BIGQUERY_DATASET)
        client.get_dataset(dataset_ref, timeout=TIMEOUT_SECONDS)
        tables: set[str] = {t.table_id for t in client.list_tables(dataset_ref, timeout=TIMEOUT_SECONDS)}
        missing: set[str] = required_tables - tables
        if not missing:
            print(f"[OK] {name} - Status 200 (Dataset '{settings.BIGQUERY_DATASET}' and all 4 tables exist)")
            return True
        else:
            print(f"[FAIL] {name} - Missing tables: {', '.join(sorted(missing))}")
            return False
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def check_vertex_ai() -> bool:
    name: str = "Vertex AI"
    try:
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
        model: GenerativeModel = GenerativeModel(settings.gemini_flash_model)
        start: float = time.perf_counter()
        model.generate_content("Reply with the single word: pong")
        latency_ms: int = int((time.perf_counter() - start) * 1000)
        print(f"[OK] {name} - Status 200 (Latency: {latency_ms}ms)")
        return True
    except Exception as exc:
        print(f"[FAIL] {name} - {type(exc).__name__}")
        return False


def main() -> None:
    checks: List[Callable[[], bool]] = [
        check_newsapi,
        check_world_bank,
        check_crunchbase,
        check_cloud_storage,
        check_bigquery,
        check_vertex_ai,
    ]
    passed: int = 0
    total: int = len(checks)
    for check in checks:
        if check():
            passed += 1
    print(f"{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
