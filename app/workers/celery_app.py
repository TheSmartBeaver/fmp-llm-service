from celery import Celery

celery = Celery(
    "flashcard_gen",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery.conf.update(task_track_started=True)