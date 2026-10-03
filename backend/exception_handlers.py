"""backend/exception_handlers.py — Registers global exception handlers for PRISMError and unhandled exceptions."""

from typing import TYPE_CHECKING
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from backend.errors import PRISMError
else:
    try:
        from backend.errors import PRISMError
    except ImportError:
        from errors import PRISMError
import structlog

logger = structlog.get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    """Call this once inside create_app() or main.py after app is created."""

    @app.exception_handler(PRISMError)
    async def prism_error_handler(request: Request, exc: PRISMError) -> JSONResponse:
        # Log internal detail at WARNING — never expose it in the response
        logger.warning(
            "prism_error",
            path=str(request.url.path),
            status_code=exc.status_code,
            error_type=type(exc).__name__,
            # detail is intentionally NOT logged at INFO — only WARNING and above
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,  # safe for client
                # detail is intentionally NOT in the response body
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            path=str(request.url.path),
            error_type=type(exc).__name__,
            # never log exc args — may contain secrets or user data
        )
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "message": "An unexpected error occurred"},
        )
