import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*")
# Si Socket.IO tourne dans FastAPI:
# from fastapi import FastAPI
# app = FastAPI()
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

def socket_notify(event: str, data: dict):
    sio.emit(event, data)