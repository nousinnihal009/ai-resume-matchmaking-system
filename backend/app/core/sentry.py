"""
Sentry error monitoring and performance tracing initialization.

Sentry is only initialized when SENTRY_DSN is set in environment
variables. In local development without a DSN, this is a no-op.

Captures:
  - All unhandled exceptions (500 errors)
  - Slow database queries (via SQLAlchemy integration)
  - HTTP request performance traces
  - Custom business events via sentry_sdk.capture_message()

Usage in route handlers:
    import sentry_sdk
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("user_id", str(user.id))
        scope.set_tag("action", "resume_upload")
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def initialize_sentry(
    dsn: str,
    environment: str,
    traces_sample_rate: float,
    profiles_sample_rate: float,
) -> None:
    """
    Initialize Sentry SDK with FastAPI, SQLAlchemy, and logging integrations.

    Args:
        dsn: Sentry project DSN. Empty string disables Sentry.
        environment: Deployment environment label (production/staging/development)
        traces_sample_rate: Fraction of transactions to trace (0.0–1.0)
        profiles_sample_rate: Fraction of traced transactions to profile (0.0–1.0)
    """
    if not dsn:
        logger.info(
            "sentry_disabled",
            reason="SENTRY_DSN not set — error monitoring inactive",
        )
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        # Do not send PII (emails, IPs) to Sentry by default
        send_default_pii=False,
        # Attach request headers and query params to error events
        # but strip Authorization headers automatically
        before_send=_before_send_filter,
    )

    logger.info(
        "sentry_initialized",
        environment=environment,
        traces_sample_rate=traces_sample_rate,
    )


def _before_send_filter(event: dict, hint: dict) -> dict:
    """
    Filter sensitive data before sending events to Sentry.

    Removes Authorization headers and password fields from
    all error events to prevent credential leakage.
    """
    request = event.get("request", {})
    headers = request.get("headers", {})

    # Strip Authorization header
    if "Authorization" in headers:
        headers["Authorization"] = "[FILTERED]"
    if "authorization" in headers:
        headers["authorization"] = "[FILTERED]"

    # Strip password fields from request body
    data = request.get("data", {})
    if isinstance(data, dict):
        for key in ("password", "confirm_password", "hashed_password"):
            if key in data:
                data[key] = "[FILTERED]"

    return event
