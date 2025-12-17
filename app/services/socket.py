import asyncio
import json
import os
import socketio
from redis.asyncio import Redis  # ⬅️ important : version async

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# Si Socket.IO tourne dans FastAPI:
# from fastapi import FastAPI
# app = FastAPI()
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

redis = Redis(host=REDIS_HOST, port=6379, decode_responses=True)

async def redis_listener():
    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe("mindmap_events")

            print("✔️ Redis listener subscribed to 'mindmap_events' channel")

            async for message in pubsub.listen():
                try:
                    print("📥 Redis message received :", message)

                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            print("📥 Will try send Notification via Socket.IO :", message)

                            await sio.emit(
                                data["event"],
                                {
                                    "task_id": data.get("task_id"),
                                    "flashcard": data,
                                    # "prompt": message["prompt"]
                                }
                            )
                            print("📥 Notification sent via Socket.IO :", data)
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON decode error: {e}")
                        except KeyError as e:
                            print(f"❌ Missing key in data: {e}")
                        except Exception as e:
                            print(f"❌ Error processing message: {e}")

                except Exception as e:
                    print(f"❌ Error in message loop: {e}")
                    continue

        except Exception as e:
            print(f"❌ Redis listener error: {e}")
            print("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        finally:
            try:
                await pubsub.unsubscribe("mindmap_events")
                await pubsub.close()
            except:
                pass

    print("🔻 Redis listener stopped")

async def socket_notify(event: str, data: dict):
    print("📥 Try to send notif A")
    await sio.emit(event, data)
    print("📥 Notification emited :", event)
    print("📥 Data emited :", data)

@sio.event
async def connect(sid, environ):
    print("✔️ Client connecté :", sid)
    await sio.emit("mindmap_events", {"msg": "Bienvenue"}, to=sid)

@sio.event
def disconnect(sid):
    print("❌ Client déconnecté :", sid)

@sio.on("generate_flashcard")
def generate_flashcard(sid, data):
    print("📥 Reçu :", data)

    # Exemple : renvoyer une flashcard
    # sio.emit("flashcard_generated", {"question": "Test", "answer": "OK"})
    # print("📤 Flashcard envoyée")