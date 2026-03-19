"""
Celery application factory.

Creates and configures the Celery instance using Redis as both
broker and result backend. Configuration is pulled from the same
pydantic-settings object used by FastAPI so environment variables
are the single source of truth.

Usage:
    # Start worker:
    celery -A app.worker.celery_app:celery worker --loglevel=info

    # Start beat (if periodic tasks are needed later):
    celery -A app.worker.celery_app:celery beat --loglevel=info
"""
from celery import Celery
from app.core.config import settings

celery = Celery(
    "resume_matcher",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# ── Celery configuration ──────────────────────────────────────────────
celery.conf.update(
    # Serialize everything as JSON for cross-language compatibility
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # UTC timestamps everywhere
    timezone="UTC",
    enable_utc=True,

    # Acknowledge tasks only after they complete (at-least-once delivery)
    task_acks_late=True,

    # One task at a time per worker process for memory-heavy ML work
    worker_prefetch_multiplier=1,

    # Soft/hard time limits to prevent runaway tasks
    task_soft_time_limit=300,   # 5 minutes soft
    task_time_limit=600,        # 10 minutes hard

    # Route tasks to dedicated queues
    task_routes={
        "app.worker.tasks.process_resume_task": {"queue": "resume_processing"},
        "app.worker.tasks.batch_match_task": {"queue": "matching"},
        "app.worker.gdpr_tasks.gdpr_delete_user_data_task": {"queue": "gdpr"},
    },

    # Result expiry — keep results for 1 hour then discard
    result_expires=3600,
)

# Auto-discover task modules
celery.autodiscover_tasks(["app.worker"])
