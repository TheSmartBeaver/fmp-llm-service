# http://127.0.0.1:8000/docs
# uvicorn app.main:app --reload 
# pip3 install -r requirements.txt
# source env/bin/activate 

from fastapi import FastAPI
import socketio
from app.routers.chat import router
from app.routers.flashcard.router import flashcard_router
from app.services.socket import sio

app = FastAPI(
    title="Freelance Bot Worker API",
    version="1.0.0",
)

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

app.include_router(router)
app.include_router(flashcard_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Freelance Bot API is running"}
