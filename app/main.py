# http://127.0.0.1:8000/docs
# uvicorn app.main:app --reload 
# pip3 install -r requirements.txt
# source env/bin/activate 

from fastapi import FastAPI
from app.routers.chat import router

app = FastAPI(
    title="Freelance Bot Worker API",
    version="1.0.0",
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Freelance Bot API is running"}
