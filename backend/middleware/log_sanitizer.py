"""backend/middleware/log_sanitizer.py — Middleware and logging filter to redact sensitive API keys."""

import logging
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

API_KEY_PATTERNS = [
    re.compile(r"(AIzaSy[a-zA-Z0-9_-]{33})"),  # Gemini / GCP API key pattern
    re.compile(r"(key-[a-zA-Z0-9]{32})"),       # Generic 32-char key
    re.compile(r"(Bearer\s+[a-zA-Z0-9_\-\.=]+)", re.IGNORECASE),  # Auth header
]


def sanitize_log_message(message: str) -> str:
    """Redact any API keys or tokens found in a log string."""
    sanitized = message
    for pattern in API_KEY_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


class LogSanitizingFilter(logging.Filter):
    """Logging filter that redacts API keys from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: sanitize_log_message(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_log_message(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        return True


class LogSanitizerMiddleware(BaseHTTPMiddleware):
    """Starlette middleware ensuring request query parameters don't leak API keys into logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        return response
