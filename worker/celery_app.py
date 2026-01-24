from celery import Celery
from shared.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['tasks'] 
)

celery_app.conf.update(
    task_routes={"correct_essay": {"queue": "correcoes"}}, 
    task_rate_limit="1/m"
)