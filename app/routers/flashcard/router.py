import json
import os
import uuid
from fastapi import APIRouter, Header
from redis import Redis
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.message import MessageRequest
from app.chains.simple_chain import run_simple_chain
from app.services.socket import socket_notify
from app.workers.tasks import generate_flashcard_task

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

flashcard_router = APIRouter(prefix="/flashcard_generation")

@flashcard_router.post("/generate")
async def ask_bot(request: UserEntryDto):
    response = run_simple_chain(request)
    return {"response": response}

@flashcard_router.post("/generate_CELERY")
async def generate_flashcard(
    instructions: UserEntryDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid")
):
    """
    Lance une génération asynchrone de flashcard via Celery.

    Args:
        instructions: UserEntryDto contenant les instructions pour la génération
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM

    Returns:
        Dict avec l'ID de la tâche et le statut
    """
    task_id = str(uuid.uuid4())
    result = generate_flashcard_task.delay(task_id, instructions.model_dump(), auth_uid)
    # generate_flashcard_task(task_id+"aaaa", instructions)
    print("Job lancé ! ID:", result.id)

    # Récupérer le résultat (bloquant)
    # print("Résultat :", result.get())
    print("📥 Task queued with ID :", task_id)
    # fake
    # await socket_notify(
    #     event="flashcard_generated",
    #     data={"task_id": "fake_task_id", "flashcard": {"question": "Fake question", "answer": "Fake answer"}}
    # )
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis.publish("flashcard_events", json.dumps({
        "event": "flashcard_generated",
        "task_id": task_id,
        "flashcard": "DOGSHIT"
    }))

    return {"task_id": task_id, "status": "queued"}
