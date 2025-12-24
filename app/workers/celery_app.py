import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

celery = Celery(
    "flashcard_gen",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
)

celery.conf.update(
    task_track_started=True,
    result_expires=3600,  # Les résultats expirent après 1 heure
    task_ignore_result=False,  # IMPORTANT: Ne pas ignorer les résultats
    task_store_eager_result=True,  # Stocker les résultats même en mode eager
    result_extended=True,  # Inclure les métadonnées dans les résultats
)

# Import tasks to register them with Celery
from app.workers import tasks