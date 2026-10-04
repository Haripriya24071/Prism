"""backend/main.py — Runnable FastAPI application with lifespan Vertex AI init and 8 route stubs."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

if TYPE_CHECKING:
    from backend.config import settings, init_vertex_ai
    from backend.logging_config import configure_logging
    from backend.exception_handlers import register_exception_handlers
    from backend.middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter
    from backend.session_store import (
        cleanup_expired_sessions,
        create_session as store_create_session,
        get_session as store_get_session,
        update_session as store_update_session,
        set_session_status as store_set_session_status,
    )
    from backend.errors import SessionNotFoundError, IntakeError
    from backend.models.intake import ChatRequest, IntakePackage, IntakeExtraction
    from backend.intake.conversation import run_conversation_turn
    from backend.intake.extractor import extract_structured_fields
    from backend.intake.vision import analyse_image
    from backend.intake.document import extract_document_text
    from backend.pipeline import run_pipeline
    from backend.sse_manager import event_generator
else:
    try:
        from backend.config import settings, init_vertex_ai
        from backend.logging_config import configure_logging
        from backend.exception_handlers import register_exception_handlers
        from backend.middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter
        from backend.session_store import (
            cleanup_expired_sessions,
            create_session as store_create_session,
            get_session as store_get_session,
            update_session as store_update_session,
            set_session_status as store_set_session_status,
        )
        from backend.errors import SessionNotFoundError, IntakeError
        from backend.models.intake import ChatRequest, IntakePackage, IntakeExtraction
        from backend.intake.conversation import run_conversation_turn
        from backend.intake.extractor import extract_structured_fields
        from backend.intake.vision import analyse_image
        from backend.intake.document import extract_document_text
        from backend.pipeline import run_pipeline
        from backend.sse_manager import event_generator
    except ImportError:
        from config import settings, init_vertex_ai
        from logging_config import configure_logging
        from exception_handlers import register_exception_handlers
        from middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter
        from session_store import (
            cleanup_expired_sessions,
            create_session as store_create_session,
            get_session as store_get_session,
            update_session as store_update_session,
            set_session_status as store_set_session_status,
        )
        from errors import SessionNotFoundError, IntakeError
        from models.intake import ChatRequest, IntakePackage, IntakeExtraction
        from intake.conversation import run_conversation_turn
        from intake.extractor import extract_structured_fields
        from intake.vision import analyse_image
        from intake.document import extract_document_text
        from pipeline import run_pipeline
        from sse_manager import event_generator

# Configure logging with sanitization
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
for handler in logging.getLogger().handlers:
    handler.addFilter(LogSanitizingFilter())

logger = logging.getLogger("prism")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vertex_ai()  # Vertex AI ADC — once at startup, never at module level
    configure_logging()
    asyncio.create_task(cleanup_expired_sessions())
    yield


app = FastAPI(
    title="PRISM API",
    version="0.1.0",
    description="Multi-modal AI swarm BRD generator — Manipal Hackathon 2026",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(LogSanitizerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
register_exception_handlers(app)


def _not_implemented():
    raise HTTPException(status_code=501, detail="not implemented yet")


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# Intake
@app.post("/intake/session", status_code=201)
async def create_session():
    sid = store_create_session()
    sess = store_get_session(sid)
    return sess


@app.get("/intake/session/{session_id}")
async def get_session(session_id: str):
    sess = store_get_session(session_id)
    if sess is None:
        raise SessionNotFoundError(session_id)
    return sess


@app.post("/intake/chat")
async def chat(request: ChatRequest) -> dict:
    session = store_get_session(request.session_id)
    if session is None:
        raise SessionNotFoundError(request.session_id)

    result = await run_conversation_turn(
        session_id=request.session_id,
        message=request.message,
        history=session["conversation_history"],
        prior_extraction=session.get("intake_package"),
    )

    extraction_data = result.get("extraction", {})
    store_update_session(
        request.session_id,
        {
            "conversation_history": result["updated_history"],
            "intake_package": extraction_data,
            "status": "ready" if result["is_complete"] else "intake",
        },
    )

    if result["is_complete"]:
        store_set_session_status(request.session_id, "ready")

    return {
        "reply": result["reply"],
        "is_complete": result["is_complete"],
        "extraction_complete": result["is_complete"],
        "turn": len(result["updated_history"]) // 2,
        "extraction": extraction_data,
        "missing_fields": result.get("missing_fields", []),
        "captured_fields": result.get("captured_fields", {}),
        "completion_pct": result.get("completion_pct", 0),
        "suggested_chips": result.get("suggested_chips", []),
    }


@app.post("/intake/upload")
async def upload(
    session_id: str,
    file: UploadFile = File(...),
) -> dict:
    session = store_get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)

    file_bytes = await file.read()

    max_bytes = getattr(settings, "max_upload_bytes", settings.MAX_UPLOAD_BYTES)
    if len(file_bytes) > max_bytes:
        raise IntakeError("File exceeds 10 MB limit")

    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        file_type = "pdf"
    elif filename.endswith((".docx", ".doc")):
        file_type = "doc"
    elif filename.endswith((".jpg", ".jpeg", ".png")):
        file_type = "image"
    else:
        raise IntakeError("Unsupported file type. Upload PDF, DOCX, JPEG, or PNG.")

    if file_type == "image":
        extracted = await analyse_image(file_bytes)
    else:
        extracted = await extract_document_text(file_bytes, file_type)

    store_update_session(session_id, {"file_context": extracted})

    return {
        "session_id": session_id,
        "file_type": file_type,
        "extracted_chars": len(extracted),
    }


# Generation
@app.post("/generate")
async def generate(session_id: str, background_tasks: BackgroundTasks) -> dict:
    session = store_get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)

    if session["status"] not in ("intake", "ready", "error", "failed"):
        return {
            "session_id": session_id,
            "status": session["status"],
            "message": "Pipeline already running or complete",
        }

    if session["status"] in ("error", "failed"):
        store_update_session(session_id, error=None)

    # Rebuild IntakePackage from session store or extract from history
    intake_data = session.get("intake_package")
    if not intake_data:
        conv = session.get("conversation_history", [])
        user_msgs = [t.get("content", "") for t in conv if t.get("role") == "user"]
        if user_msgs:
            idea_text = " ".join(user_msgs)
            try:
                extraction = await extract_structured_fields(idea_text)
                intake_data = extraction.model_dump()
            except Exception:
                intake_data = {"raw_idea": idea_text}
            store_update_session(session_id, {"intake_package": intake_data, "status": "ready"})
            session["intake_package"] = intake_data
        elif session.get("file_context"):
            intake_data = {"raw_idea": session["file_context"][:1000]}
            store_update_session(session_id, {"intake_package": intake_data, "status": "ready"})
            session["intake_package"] = intake_data
        else:
            raise IntakeError("No intake data found — please pitch your idea first")

    from datetime import datetime
    created_at_val = session["created_at"]
    if isinstance(created_at_val, str):
        created_at_dt = datetime.fromisoformat(created_at_val)
    else:
        created_at_dt = created_at_val

    intake = IntakePackage(
        session_id=session_id,
        extraction=IntakeExtraction(**intake_data) if isinstance(intake_data, dict) else IntakeExtraction(raw_idea=str(intake_data)),
        conversation_history=session.get("conversation_history", []),
        created_at=created_at_dt,
    )

    store_set_session_status(session_id, "generating")
    background_tasks.add_task(run_pipeline, session_id, intake)

    return {
        "session_id": session_id,
        "status": "generating",
        "stream_url": f"/generate/stream/{session_id}",
    }


@app.get("/generate/stream/{session_id}")
async def generate_stream(session_id: str) -> StreamingResponse:
    session = store_get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)

    return StreamingResponse(
        event_generator(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# BRD
@app.get("/brd/{session_id}")
async def get_brd(session_id: str) -> dict:
    session = store_get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)

    if session.get("brd") is None:
        # Fallback: check GCS if session was created in a separate process or worker
        try:
            from backend.gcp.storage import read_json
            gcs_brd = await read_json(session_id, "merged_brd")
            if gcs_brd:
                session["brd"] = gcs_brd
                session["status"] = "complete"
        except Exception:
            pass

    if session["status"] != "complete":
        return {
            "session_id": session_id,
            "status": session["status"],
            "brd": None,
            "message": "BRD not ready yet",
        }

    return {
        "session_id": session_id,
        "status": "complete",
        "brd": session.get("brd"),
        "investor_readiness_score": session.get("score"),
        "heatmap": session.get("heatmap"),
        "pivots": session.get("pivots", []),
        "investor_score": session.get("investor_score"),
        "context": session.get("context") or session.get("context_package"),
        "agent_outputs": session.get("agent_outputs", []),
        "score_matrix": session.get("score_matrix"),
    }


@app.get("/brd/{session_id}/pdf")
async def get_pdf(session_id: str, view: str = "final", format: str = "binary"):
    session = store_get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)

    valid_views = ("investor", "technical", "regulatory", "final", "full", "deliberation")
    if view not in valid_views:
        raise HTTPException(status_code=400, detail=f"view must be one of: {', '.join(valid_views)}")

    target_view = "final" if view in ("final", "full") else view

    pdf_urls = session.get("pdf_urls", {})
    url = pdf_urls.get(target_view)

    # If JSON explicitly requested and a public HTTP(S) URL is available
    if format == "json" and url and (url.startswith("http://") or url.startswith("https://")):
        return {
            "session_id": session_id,
            "view": target_view,
            "url": url,
            "available": True,
        }

    brd_data = session.get("brd")
    if not brd_data:
        # Fallback: check GCS if session was created in a separate process or worker
        try:
            from backend.gcp.storage import read_json
            gcs_brd = await read_json(session_id, "merged_brd")
            if gcs_brd:
                brd_data = gcs_brd
                session["brd"] = gcs_brd
        except Exception:
            pass

    if not brd_data:
        return {
            "session_id": session_id,
            "view": target_view,
            "url": None,
            "available": False,
            "message": "BRD has not been generated for this session yet",
        }

    try:
        from backend.models.brd import MergedBRD
        from backend.output.pdf_export import generate_pdf
    except ImportError:
        from models.brd import MergedBRD
        from output.pdf_export import generate_pdf

    try:
        merged_brd = MergedBRD(**brd_data) if isinstance(brd_data, dict) else brd_data
    except Exception as exc:
        logger.warning(f"failed_to_parse_merged_brd_for_pdf: {exc}")
        from backend.models.brd import BRDSection, LineageTag
        from backend.models.agents import AgentPersona
        sections = []
        for s in brd_data.get("sections", []):
            sections.append(BRDSection(
                title=s.get("title", "Section"),
                content=s.get("content", ""),
                lineage=LineageTag(
                    source_agent=AgentPersona.VC,
                    confidence=0.85,
                    data_citation="[SOURCE: system]"
                )
            ))
        merged_brd = MergedBRD(session_id=session_id, sections=sections)

    pdf_bytes = await generate_pdf(merged_brd, target_view)
    filename = "prism-master-brd.pdf" if target_view == "final" else f"prism-brd-{target_view}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


# ── Preset Cache Endpoints for Demonstrations ──────────────────────────
@app.get("/presets/cache")
async def get_preset_cache_status():
    """Return status of all pre-cached demo presets."""
    try:
        from backend.preset_cache import get_all_cached_status
    except ImportError:
        from preset_cache import get_all_cached_status
    return {"cached": get_all_cached_status()}


@app.post("/presets/instant-demo")
async def launch_instant_demo(preset: str = "b2b_code_review"):
    """Instantly initialize a session with a cached preset run for rapid demonstration."""
    try:
        from backend.preset_cache import get_cached_run
    except ImportError:
        from preset_cache import get_cached_run

    cached_data = get_cached_run(preset)
    if not cached_data:
        raise HTTPException(status_code=404, detail=f"No cached run found for preset '{preset}'")

    session_id = store_create_session()
    store_update_session(session_id, cached_data)
    store_set_session_status(session_id, "complete")

    return {
        "session_id": session_id,
        "status": "complete",
        "preset": preset,
        "is_cached": True,
        "data": cached_data,
    }

