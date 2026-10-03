"""backend/logging_config.py — Structlog setup callable once at startup."""

import logging
import structlog
from backend.config import settings


def configure_logging() -> None:
    """Call once at app startup inside lifespan. Sets up structlog with JSON output in prod, pretty in dev."""

    log_level = logging.getLevelName(settings.log_level.upper())

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
    ]

    if settings.env == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also set stdlib logging level so uvicorn logs are consistent
    logging.basicConfig(level=log_level)
