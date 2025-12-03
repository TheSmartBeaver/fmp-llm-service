import json
from redis import Redis
import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# Si Socket.IO tourne dans FastAPI:
# from fastapi import FastAPI
# app = FastAPI()
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

redis = Redis(host="localhost", port=6379, decode_responses=True)

async def redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("flashcard_events")

    async for message in pubsub.listen():
        print("📥 Redis message received :", message)
        if message["type"] == "message":
            data = json.loads(message["data"])

            await sio.emit(
                data["event"],
                {
                    "task_id": data["task_id"],
                    "flashcard": data["flashcard"]
                }
            )

async def socket_notify(event: str, data: dict):
    print("📥 Try to send notif A")
    await sio.emit(event, data)
    print("📥 Notification emited :", event)
    print("📥 Data emited :", data)

@sio.event
async def connect(sid, environ):
    print("✔️ Client connecté :", sid)
    await sio.emit("flashcard_generated", {"msg": "Bienvenue"}, to=sid)

@sio.event
def disconnect(sid):
    print("❌ Client déconnecté :", sid)

@sio.on("generate_flashcard")
def generate_flashcard(sid, data):
    print("📥 Reçu :", data)

    # Exemple : renvoyer une flashcard
    # sio.emit("flashcard_generated", {"question": "Test", "answer": "OK"})
    # print("📤 Flashcard envoyée")