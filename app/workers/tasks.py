import asyncio
import json
import os

from redis import Redis

from app.models.dto.user_entry.user_entry_dto import UserEntryDto

from .celery_app import celery
from app.chains.generator import generate_flashcard
from app.services.socket import socket_notify

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

@celery.task(name="generate.flashcard")
def generate_flashcard_task(task_id: str, instructions: UserEntryDto):
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print("📥 Starting generation")

    # Run async flashcard generator
    flashcard = generate_flashcard(instructions)

    print("📥 Generation ended")

    # Run async socket notification

    redis.publish("flashcard_events", json.dumps({
        "event": "flashcard_generated",
        "task_id": task_id,
        "flashcard": flashcard
    }))

    print("📥 Celery task ended")

    return flashcard
