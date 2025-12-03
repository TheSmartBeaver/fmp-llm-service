import asyncio
from .celery_app import celery
from app.chains.generator import generate_flashcard
from app.services.socket import socket_notify

@celery.task(name="generate.flashcard")
def generate_flashcard_task(task_id: str, instructions: dict):
    print("📥 Starting generation")

    # Run async flashcard generator
    flashcard = generate_flashcard(instructions)

    print("📥 Generation ended")

    # Run async socket notification
    asyncio.run(socket_notify(
        event="flashcard_generated",
        data={"task_id": task_id, "flashcard": flashcard}
    ))

    print("📥 Celery task ended")

    return flashcard
