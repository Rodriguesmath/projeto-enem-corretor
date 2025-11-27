import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=['tasks'] 
)

celery_app.conf.update(
    task_routes={"correct_essay": {"queue": "correcoes"}}, 
    task_rate_limit="1/m"
)