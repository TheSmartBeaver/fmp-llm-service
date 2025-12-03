from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.services.socket import redis_listener

@asynccontextmanager
async def customlifespan(app: FastAPI):
    # 🚀 Start Redis listener
    print("✔️ Redis listener starting")
    await redis_listener()
    task = asyncio.create_task(redis_listener())
    # await redis_listener()
    print("✔️ Redis listener started")
    yield  # Application is running here

    # 🔻 Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
