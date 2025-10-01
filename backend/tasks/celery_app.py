# backend/tasks/celery_app.py
from celery import Celery
from ..config import REDIS_URL # <--- NEW IMPORT

celery_app = Celery(
    "backend", 
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Serialization settings
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# Ensure Celery knows about your tasks (pointing to the new 'workers' folder)
celery_app.autodiscover_tasks(["backend.tasks.workers"], related_name='tasks')