import uuid
from fastapi import APIRouter
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.message import MessageRequest
from app.chains.simple_chain import run_simple_chain
from app.workers.tasks import generate_flashcard_task

flashcard_router = APIRouter(prefix="/flashcard_generation")

@flashcard_router.post("/generate")
async def ask_bot(request: UserEntryDto):
    response = run_simple_chain(request)
    return {"response": response}

@flashcard_router.post("/generate_CELERY")
async def generate_flashcard(instructions: dict):
    task_id = str(uuid.uuid4())
    generate_flashcard_task.delay(task_id, instructions)

    return {"task_id": task_id, "status": "queued"}
