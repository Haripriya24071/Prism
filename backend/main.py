"""backend/main.py — Runnable FastAPI application with lifespan Vertex AI init and 8 route stubs."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from backend.config import settings, init_vertex_ai
    from backend.logging_config import configure_logging
    from backend.exception_handlers import register_exception_handlers
    from backend.middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter
    from backend.session_store import (
        cleanup_expired_sessions,
        create_session as store_create_session,
        get_session as store_get_session,
    )
    from backend.errors import SessionNotFoundError
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
        )
        from backend.errors import SessionNotFoundError
    except ImportError:
        from config import settings, init_vertex_ai
        from logging_config import configure_logging
        from exception_handlers import register_exception_handlers
        from middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter
        from session_store import (
            cleanup_expired_sessions,
            create_session as store_create_session,
            get_session as store_get_session,
        )
        from errors import SessionNotFoundError

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
async def chat(session_id: str):
    _not_implemented()


@app.post("/intake/upload")
async def upload(session_id: str):
    _not_implemented()


# Generation
@app.post("/generate")
async def generate(session_id: str):
    _not_implemented()


@app.get("/generate/stream/{session_id}")
async def generate_stream(session_id: str):
    _not_implemented()


# BRD
@app.get("/brd/{session_id}")
async def get_brd(session_id: str):
    _not_implemented()


@app.get("/brd/{session_id}/pdf")
async def get_pdf(session_id: str, view: str = "investor"):
    _not_implemented()
