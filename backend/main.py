"""backend/main.py — Runnable FastAPI application with lifespan Vertex AI init and 8 route stubs."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

from backend.config import settings, init_vertex_ai
from backend.exception_handlers import register_exception_handlers
from backend.middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter

# Configure logging with sanitization
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
for handler in logging.getLogger().handlers:
    handler.addFilter(LogSanitizingFilter())

logger = logging.getLogger("prism")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vertex_ai()  # Vertex AI ADC — once at startup, never at module level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL.upper())
        ),
    )
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
    _not_implemented()


@app.get("/intake/session/{session_id}")
async def get_session(session_id: str):
    _not_implemented()


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
