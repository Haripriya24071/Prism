"""backend/gcp/storage.py — Google Cloud Storage read/write helpers."""


async def write_json(session_id: str, filename: str, data: dict) -> str:
    raise NotImplementedError("Phase 10")


async def read_json(session_id: str, filename: str) -> dict | None:
    raise NotImplementedError("Phase 10")


async def write_pdf(session_id: str, filename: str, pdf_bytes: bytes, view: str) -> str:
    raise NotImplementedError("Phase 10")
