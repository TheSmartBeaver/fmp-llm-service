from fastapi import APIRouter
from app.models.message import MessageRequest
from app.chains.simple_chain import run_simple_chain

router = APIRouter(prefix="/api")

@router.post("/ask")
async def ask_bot(request: MessageRequest):
    response = run_simple_chain(request.message)
    return {"response": response}

