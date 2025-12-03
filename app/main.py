# http://127.0.0.1:8000/docs
# uvicorn app.main:app --reload 
# pip3 install -r requirements.txt
# source env/bin/activate 
# uvicorn main:app --host 127.0.0.1 --port 8003 --reload

import os
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
import socketio
from app.routers.chat import router
from app.routers.flashcard.router import flashcard_router
from app.services.lifespan import customlifespan
from app.services.socket import sio

load_dotenv(find_dotenv())
print(find_dotenv())

app = FastAPI(
    title="FMP LLM Service",
    version="1.0.0",
    lifespan=customlifespan
)

socket_app = socketio.ASGIApp(sio, other_asgi_app=None)

app.mount("/socket.io", socket_app)

app.include_router(router)
app.include_router(flashcard_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Freelance Bot API is running"}