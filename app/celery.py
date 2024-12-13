from celery import Celery

from app.config.settings import CELERY_BACKEND, CELERY_BROKER

app = Celery("app", broker=CELERY_BROKER, backend=CELERY_BACKEND)

app.conf.update(
    task_default_queue="default",
    result_expires=300,
)

app.autodiscover_tasks(["app.tasks"])
