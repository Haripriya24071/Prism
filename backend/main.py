"""backend/main.py — FastAPI application entry point and thin orchestrator."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.errors import PrismException
from backend.middleware.log_sanitizer import LogSanitizerMiddleware, LogSanitizingFilter

# Configure logging with sanitization
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
for handler in logging.getLogger().handlers:
    handler.addFilter(LogSanitizingFilter())

logger = logging.getLogger("prism")

app = FastAPI(
    title="PRISM API",
    description="Multi-Modal AI Swarm BRD Generator Backend",
    version="1.0.0",
)

# Middleware
app.add_middleware(LogSanitizerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PrismException)
async def prism_exception_handler(request: Request, exc: PrismException):
    """Global exception handler for all typed PRISM errors."""
    logger.error(f"PrismException caught on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status_code": exc.status_code},
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint returning service status and model configuration."""
    return {
        "status": "healthy",
        "service": "PRISM Backend",
        "models": {
            "flash": settings.GEMINI_FLASH_MODEL,
            "pro": settings.GEMINI_PRO_MODEL,
        },
        "gcp": {
            "project_id": settings.GCP_PROJECT_ID,
            "region": settings.GCP_REGION,
        },
    }
