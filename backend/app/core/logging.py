"""
Logging configuration for the application.
Uses structlog for structured logging.
"""
import logging
import sys
from typing import Any, Dict

try:
    import structlog
    from structlog.stdlib import LogRecord
    from structlog.processors import JSONRenderer
    from structlog.dev import ConsoleRenderer
except ImportError:
    structlog = None

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    """
    if structlog is None:
        # Fallback to basic logging if structlog not available
        logging.basicConfig(
            level=logging.INFO if not settings.DEBUG else logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        return

    # Configure structlog
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.DEBUG:
        # Development: human-readable console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> Any:
    """
    Get a configured logger instance.
    """
    if structlog is None:
        return logging.getLogger(name)
    return structlog.get_logger(name)
