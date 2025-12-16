import asyncio
import json
import os

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv, find_dotenv

from app.models.dto.user_entry.user_entry_dto import UserEntryDto

from .celery_app import celery
from app.chains.generator import generate_flashcard
from app.chains.llm.open_ai_gpt4o_mini_llm import OpenAiGPT4oMiniLlm
from app.chains.mind_map_generator import MindMapGenerator
from app.services.socket import socket_notify

# Load environment variables
load_dotenv(find_dotenv())

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Database configuration for Celery worker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:rambaudin@fmp_postgres:5432/FlashMemProDb")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load embedding model and LLM for mind map generation
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)
openai_llm = OpenAiGPT4oMiniLlm().get_llm()

@celery.task(name="generate.flashcard")
def generate_flashcard_task(task_id: str, instructions: dict):
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print("📥 Starting generation")

    # Reconstruct UserEntryDto from dict
    instructions_dto = UserEntryDto(**instructions)
    print(f"📥 UserEntryDto reconstructed: {instructions_dto}")

    # Run async flashcard generator
    flashcard = generate_flashcard(instructions_dto)

    print("📥 Generation ended")

    # Run async socket notification

    redis.publish("flashcard_events", json.dumps({
        "event": "flashcard_generated",
        "task_id": task_id,
        "flashcard": flashcard
    }))

    print("📥 Celery task ended")

    return flashcard


@celery.task(name="generate.mindmap")
def generate_mindmap_task(task_id: str, raw_data: str, top_k: int = 15):
    """
    Tâche Celery pour générer une carte mentale.

    Args:
        task_id: Identifiant unique de la tâche
        raw_data: Données pédagogiques brutes
        top_k: Nombre de templates à utiliser

    Returns:
        Dict contenant la carte mentale générée
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting mindmap generation for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Create mind map generator
        generator = MindMapGenerator(
            db_session=db,
            llm=openai_llm,
            embedding_model=embedding_model
        )

        # Generate mind map
        mind_map = generator.generate_mind_map(
            raw_data=raw_data,
            top_k=top_k
        )

        print(f"📥 Mindmap generation completed for task {task_id}")

        # Publish result to Redis
        redis.publish("mindmap_events", json.dumps({
            "event": "mindmap_generated",
            "type": "message",
            "task_id": task_id,
            "mind_map": mind_map,
            "templates_used": top_k
        }))

        print(f"📥 Celery task ended for {task_id}")

        return {
            "success": True,
            "mind_map": mind_map,
            "templates_used": top_k
        }

    except Exception as e:
        print(f"❌ Error generating mindmap for task {task_id}: {str(e)}")

        # Publish error to Redis
        redis.publish("mindmap_events", json.dumps({
            "event": "mindmap_error",
            "task_id": task_id,
            "error": str(e)
        }))

        raise

    finally:
        # Close database session
        db.close()
