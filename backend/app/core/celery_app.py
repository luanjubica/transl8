from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "transl8",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.parse_document",
        "app.workers.translate_document",
        "app.workers.export_document"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
)

# Task routes (optional - for task prioritization)
celery_app.conf.task_routes = {
    "app.workers.parse_document.*": {"queue": "parsing"},
    "app.workers.translate_document.*": {"queue": "translation"},
    "app.workers.export_document.*": {"queue": "export"},
}
