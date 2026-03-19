"""
Structured JSON logging configuration using structlog.

Configures structlog to output JSON-formatted log records in production
and human-readable colored output in development (DEBUG=true).

Usage:
    from app.core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("user_logged_in", user_id=str(user.id), email=user.email)

All log calls use keyword arguments for structured fields.
Never use f-strings or string concatenation in log messages —
pass context as keyword arguments so they appear as JSON fields.
"""
import logging
import sys
import structlog
from app.core.config import settings


def configure_logging() -> None:
    """
    Configure structlog and stdlib logging.
    Call once at application startup before any logger is used.
    """
    log_level = logging.DEBUG if settings.debug else logging.INFO

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.debug:
        # Human-readable colored output for local development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON output for production log aggregators
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress noisy third-party loggers in production
    if not settings.debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Return a structlog bound logger for the given module name.

    Args:
        name: Module name, typically __name__

    Returns:
        A structlog BoundLogger instance
    """
    return structlog.get_logger(name)
