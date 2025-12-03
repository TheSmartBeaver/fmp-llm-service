import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*")
# Si Socket.IO tourne dans FastAPI:
# from fastapi import FastAPI
# app = FastAPI()
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

def socket_notify(event: str, data: dict):
    sio.emit(event, data)

@sio.event
def connect(sid, environ):
    print("✔️ Client connecté :", sid)

@sio.event
def disconnect(sid):
    print("❌ Client déconnecté :", sid)

@sio.on("generate_flashcard")
def generate_flashcard(sid, data):
    print("📥 Reçu :", data)

    # Exemple : renvoyer une flashcard
    sio.emit("flashcard_generated", {"question": "Test", "answer": "OK"})
    print("📤 Flashcard envoyée")