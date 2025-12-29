import asyncio
import json
import os

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv, find_dotenv

from app.chains.llm.claude_haiku_45_llm import ClaudeHaiku45Llm
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.llm.open_ai_o3_llm import OpenAiO3Llm
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.db.fmp_models import AppUsers, DeviceTokens

from .celery_app import celery
from app.chains.generator import generate_flashcard
from app.chains.llm.open_ai_gpt5_nano_llm import OpenAiGPT5NanoLlm
from app.chains.mind_map_generator import MindMapGenerator
from app.chains.course_material_generator import CourseMaterialGenerator
from app.services.socket import socket_notify
from app.services.fcm_service import FCMService

from app.utils.test import shit_test

# Load environment variables
load_dotenv(find_dotenv())

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Database configuration for Celery worker
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:rambaudin@fmp_postgres:5432/FlashMemProDb"
)
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load embedding model and LLM for mind map generation
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)
openai_llm = ClaudeHaiku45Llm().get_llm()


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

    redis.publish(
        "flashcard_events",
        json.dumps(
            {"event": "flashcard_generated", "task_id": task_id, "flashcard": flashcard}
        ),
    )

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
            db_session=db, llm=openai_llm, embedding_model=embedding_model
        )

        # Generate mind map
        result = generator.generate_mind_map(raw_data=raw_data, top_k=top_k)

        print(f"📥 Mindmap generation completed for task {task_id}")

        # Publish result to Redis
        redis.publish(
            "mindmap_events",
            json.dumps(
                {
                    "event": "mindmap_generated",
                    "type": "message",
                    "task_id": task_id,
                    # "mind_map": mind_map,
                    "templates_used": top_k,
                    "data": result["mind_map"],
                    "prompt": result["prompt"],
                }
            ),
        )

        print(f"📥 Celery task ended for {task_id}")

        return {
            "success": True,
            "mind_map": result["mind_map"],
            "templates_used": top_k,
            "prompt": result["prompt"],
        }

    except Exception as e:
        print(f"❌ Error generating mindmap for task {task_id}: {str(e)}")

        # Publish error to Redis
        redis.publish(
            "mindmap_events",
            json.dumps({"event": "mindmap_error", "task_id": task_id, "error": str(e)}),
        )

        raise

    finally:
        # Close database session
        db.close()


@celery.task(name="generate.course_material")
def generate_course_material_task(
    task_id: str, user_entry_dict: dict, auth_uid: str, top_k: int = 15
):
    """
    Tâche Celery pour générer un support de cours et envoyer une notification FCM.

    Args:
        task_id: Identifiant unique de la tâche
        user_entry_dict: Dictionnaire UserEntryDto contenant le contexte, le contenu et les médias
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
        top_k: Nombre de templates à utiliser

    Returns:
        Dict contenant les supports de cours générés
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting course material generation for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct UserEntryDto from dict
        user_entry = UserEntryDto(**user_entry_dict)
        print(f"📥 UserEntryDto reconstructed: {user_entry}")

        # Create course material generator
        generator = CourseMaterialGenerator(
            db_session=db, llm=openai_llm, embedding_model=embedding_model
        )

        # Generate course material
        # result = generator.generate_course_material(
        #     user_entry=user_entry,
        #     top_k=top_k
        # )

        #MOCK DATA for debugging FCM
        result = {
            "success": True,
            "supports": [
                {
                    "support": shit_test,
                    "version": "1.0.0",
                },
                {
                    "support": {
                        "template_name": "conceptual/theorie",
                        "icon": "🔬",
                        "label": "THÉORIE",
                        "title": "Photosynthèse",
                        "description": [
                            "La photosynthèse est le processus par lequel les plantes, les algues et certaines bactéries convertissent l'énergie lumineuse en énergie chimique stockée, principalement sous forme de glucides. Ce processus a lieu essentiellement dans les chloroplastes des cellules végétales et comprend des réactions photochimiques localisées dans les thylakoïdes (phase lumineuse) et des réactions biochimiques dans le stroma (phase sombre ou cycle de Calvin).",
                            {
                                "template_name": "text/detail_technique",
                                "icon": "🖼️",
                                "text": "Image illustrative — schéma détaillé d'un chloroplaste montrant les thylakoïdes et le stroma. URL: https://example.com/images/chloroplaste.png",
                            },
                        ],
                    },
                    "version": "1.0.0",
                },
            ],
            "templates_used": 15,
            "prompt": "TO DO: long prompt here...",
        }

        print(f"📥 Course material generation completed for task {task_id}")

        # Publish result to Redis (keep for backward compatibility)
        redis.publish(
            "course_material_events",
            json.dumps(
                {
                    "event": "course_material_generated",
                    "type": "message",
                    "task_id": task_id,
                    "templates_used": top_k,
                    "data": result["supports"],
                    "prompt": result["prompt"],
                }
            ),
        )

        # Send FCM notification
        user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
        if user:
            active_devices = (
                db.query(DeviceTokens)
                .filter(
                    DeviceTokens.AppUserSKU == user.SKU, DeviceTokens.IsActive == True
                )
                .all()
            )

            if active_devices:
                fcm_service = FCMService()
                tokens = [device.FcmToken for device in active_devices]

                supports_count = (
                    len(result["supports"])
                    if isinstance(result["supports"], list)
                    else 1
                )

                # Send only metadata in FCM notification (Android has 4KB limit)
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Supports de cours générés",
                    body=f"{supports_count} support(s) de cours ont été générés avec succès",
                    data={
                        "task_id": task_id,
                        "event": "course_material_generated",
                        "templates_used": str(top_k),
                        "supports_count": str(supports_count),
                        # Don't send full data, app will fetch from Redis/API using task_id
                    },
                    notification_id=task_id,
                )

                print(
                    f"📱 FCM notifications sent: {fcm_result['success_count']} succeeded, {fcm_result['failure_count']} failed"
                )
            else:
                print(f"⚠️ No active devices found for user {auth_uid}")
        else:
            print(f"⚠️ User not found with auth_uid: {auth_uid}")

        print(f"📥 Celery task ended for {task_id}")

        return {
            "success": True,
            "supports": result["supports"],
            "templates_used": top_k,
            "prompt": result["prompt"],
        }

    except Exception as e:
        print(f"❌ Error generating course material for task {task_id}: {str(e)}")

        # Publish error to Redis
        redis.publish(
            "course_material_events",
            json.dumps(
                {"event": "course_material_error", "task_id": task_id, "error": str(e)}
            ),
        )

        # Send FCM error notification
        try:
            user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
            if user:
                active_devices = (
                    db.query(DeviceTokens)
                    .filter(
                        DeviceTokens.AppUserSKU == user.SKU,
                        DeviceTokens.IsActive == True,
                    )
                    .all()
                )

                if active_devices:
                    fcm_service = FCMService()
                    tokens = [device.FcmToken for device in active_devices]

                    fcm_service.send_multicast_notification(
                        tokens=tokens,
                        title="Erreur de génération",
                        body="Une erreur s'est produite lors de la génération des supports de cours",
                        data={
                            "task_id": task_id,
                            "event": "course_material_error",
                            "error": str(e),
                        },
                        notification_id=task_id,
                    )
        except Exception as fcm_error:
            print(f"❌ Error sending FCM error notification: {str(fcm_error)}")

        raise

    finally:
        # Close database session
        db.close()
