from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "tasks",
    broker=settings.REDIS.CELERY_URL,
    include=[
        "app.tasks.clean_unverified_users",
    ],
)


celery.conf.beat_schedule = {
    'cleanup-unverified-users-daily': {
        'task': 'app.tasks.clean_unverified_users.task_cleanup_unverified_users',
        'schedule': crontab(hour=23, minute=0),
    },
}

celery.conf.update(
    task_serializer="json",
    accept_content=["application/json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
