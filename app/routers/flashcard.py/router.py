from fastapi import APIRouter
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.message import MessageRequest
from app.chains.simple_chain import run_simple_chain

router = APIRouter(prefix="/flashcard_generation")

@router.post("/generate")
async def ask_bot(request: UserEntryDto):
    response = run_simple_chain(request)
    return {"response": response}

