from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "wallet_tasks",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_routes={
        "tasks.settle_transaction": {"queue": "settlement"},
        "tasks.retry_failed": {"queue": "retry"},
    },
    task_default_queue="default",
    result_expires=3600,
)

@celery_app.task
def health_check():
    return "ok"
