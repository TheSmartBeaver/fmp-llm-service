import asyncio
import json
import os

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv, find_dotenv

from app.chains.llm.openai_codex_llm import OpenAICodexLLM
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.llm.open_ai_o3_llm import OpenAiO3Llm
from app.chains.llm.universal_llm import create_universal_llm
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.dto.user_entry.pedagogical_context_entry_dto import PedagogicalContextEntryDto
from app.models.dto.user_entry.flashcard_modification_entry_dto import FlashcardModificationEntryDto
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.quiz.quiz_dto import QuizGenerationRequestDto, QuizItemDto, QuizOutputItemDto, shuffle_quiz_item_answers
from app.models.db.fmp_models import AppUsers, DeviceTokens

from .celery_app import celery
from app.chains.generator import generate_flashcard
from app.chains.llm.open_ai_gpt5_nano_llm import OpenAiGPT5NanoLlm
from app.chains.mind_map_generator import MindMapGenerator
from app.chains.course_material_generator import CourseMaterialGenerator
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2
from app.chains.course_material_generator_v3 import CourseMaterialGeneratorV3
from app.services.socket import socket_notify
from app.services.fcm_service import FCMService

from app.utils.test import shit_test

from app.utils.test import shit_test_4

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
openai_llm = create_universal_llm("gpt-5.1-codex-mini")


@celery.task(name="generate.flashcard")
def generate_flashcard_task(task_id: str, instructions: dict, auth_uid: str):
    """
    Tâche Celery pour générer une flashcard et envoyer une notification FCM.

    Args:
        task_id: Identifiant unique de la tâche
        instructions: Dictionnaire UserEntryDto contenant les instructions
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM

    Returns:
        Dict contenant la flashcard générée
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting flashcard generation for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct UserEntryDto from dict
        instructions_dto = UserEntryDto(**instructions)
        print(f"📥 UserEntryDto reconstructed: {instructions_dto}")

        # Run async flashcard generator
        flashcard = generate_flashcard(instructions_dto)

        print(f"📥 Flashcard generation completed for task {task_id}")

        # Publish result to Redis
        redis.publish(
            "flashcard_events",
            json.dumps(
                {"event": "flashcard_generated", "task_id": task_id, "flashcard": flashcard}
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

                # Send FCM notification
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Flashcard générée",
                    body="Votre flashcard a été générée avec succès",
                    data={
                        "task_id": task_id,
                        "event": "flashcard_generated",
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

        return flashcard

    except Exception as e:
        print(f"❌ Error generating flashcard for task {task_id}: {str(e)}")

        # Publish error to Redis
        redis.publish(
            "flashcard_events",
            json.dumps(
                {"event": "flashcard_error", "task_id": task_id, "error": str(e)}
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
                        body="Une erreur s'est produite lors de la génération de la flashcard",
                        data={
                            "task_id": task_id,
                            "event": "flashcard_error",
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


@celery.task(name="generate.flashcard_from_pedag")
def generate_flashcard_from_pedag_task(task_id: str, pedag_entry_dict: dict, auth_uid: str, top_k: int = 12):
    """
    Tâche Celery pour générer des flashcards à partir d'un JSON pédagogique.

    Args:
        task_id: Identifiant unique de la tâche
        pedag_entry_dict: Dictionnaire PedagogicalContextEntryDto contenant le contexte et le JSON pédagogique
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
        top_k: Nombre de templates à utiliser

    Returns:
        Dict contenant les flashcards générées
    """
    print(f"📥 Starting flashcard from pedagogical JSON generation for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct PedagogicalContextEntryDto from dict
        pedag_entry = PedagogicalContextEntryDto(**pedag_entry_dict)
        print(f"📥 PedagogicalContextEntryDto reconstructed: {pedag_entry}")

        # Create mind map generator
        generator = MindMapGenerator(
            db_session=db, llm=openai_llm, embedding_model=embedding_model
        )

        # Generate mind map using _generate_info_format_pairs with pedagogical_json as raw_data
        # Pass additional_instructions from context to guide triplet creation
        result = generator.generate_mind_map(
            raw_data=pedag_entry.pedagogical_json,
            top_k=top_k,
            additional_instructions=pedag_entry.context.additional_instructions
        )
        # result = {
        #     "mind_map": shit_test_4,
        #     "prompt": "SHIT"
        # }

        print(f"📥 Flashcard from pedagogical JSON generation completed for task {task_id}")

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

                # Send FCM notification with metadata only (app will fetch result using task_id)
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Flashcards générées",
                    body="Vos flashcards ont été générées avec succès",
                    data={
                        "task_id": task_id,
                        "event": "flashcard_from_pedag_generated",
                        "templates_used": str(top_k),
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
            "mind_map": result["mind_map"],
            "templates_used": top_k,
            "prompt": result["prompt"],
        }

    except Exception as e:
        print(f"❌ Error generating flashcard from pedagogical JSON for task {task_id}: {str(e)}")

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
                        body="Une erreur s'est produite lors de la génération des flashcards",
                        data={
                            "task_id": task_id,
                            "event": "flashcard_from_pedag_error",
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


@celery.task(name="modify.flashcard")
def modify_flashcard_task(task_id: str, fc_entry_dict: dict, auth_uid: str, top_k: int = 12):
    """
    Tâche Celery pour modifier une flashcard existante selon des instructions.

    Args:
        task_id: Identifiant unique de la tâche
        fc_entry_dict: Dictionnaire FlashcardModificationEntryDto contenant le JSON de la carte et les instructions
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
        top_k: Nombre de templates à utiliser

    Returns:
        Dict contenant la flashcard modifiée
    """
    print(f"📥 Starting flashcard modification for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct FlashcardModificationEntryDto from dict
        fc_entry = FlashcardModificationEntryDto(**fc_entry_dict)
        print(f"📥 FlashcardModificationEntryDto reconstructed: {fc_entry}")

        # Create mind map generator
        generator = MindMapGenerator(
            db_session=db, llm=openai_llm, embedding_model=embedding_model
        )

        # Modify the flashcard
        result = generator.modify_flashcard(
            flashcard_json=fc_entry.flashcard_json,
            modification_instructions=fc_entry.modification_instructions,
            top_k=top_k
        )

        print(f"📥 Flashcard modification completed for task {task_id}")

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

                # Send FCM notification with metadata only
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Flashcard modifiée",
                    body="Votre flashcard a été modifiée avec succès",
                    data={
                        "task_id": task_id,
                        "event": "flashcard_modified",
                        "templates_used": str(top_k),
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
            "mind_map": result["mind_map"],
            "templates_used": top_k,
            "prompt": result["prompt"],
        }

    except Exception as e:
        print(f"❌ Error modifying flashcard for task {task_id}: {str(e)}")

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
                        title="Erreur de modification",
                        body="Une erreur s'est produite lors de la modification de la flashcard",
                        data={
                            "task_id": task_id,
                            "event": "flashcard_modification_error",
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


@celery.task(name="generate.course_material")
def generate_course_material_task(
    task_id: str, user_entry_dict: dict, auth_uid: str, llm_config_dict: dict = None, top_k: int = 20
):
    """
    Tâche Celery pour générer un support de cours avec CourseMaterialGeneratorV2 et envoyer une notification FCM.

    Cette version utilise le nouveau générateur V2 qui:
    - Crée d'abord un JSON pédagogique enrichi avec explications complètes
    - Utilise TemplateStructureGenerator pour mapper vers des templates de manière cohérente
    - Produit une structure globale cohérente

    Args:
        task_id: Identifiant unique de la tâche
        user_entry_dict: Dictionnaire UserEntryDto contenant le contexte, le contenu et les médias
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
        llm_config_dict: Dictionnaire LLMConfigDto optionnel pour la configuration des modèles LLM
        top_k: Nombre de templates à utiliser (défaut: 20)

    Returns:
        Dict contenant le support de cours généré
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting course material generation V2 for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct UserEntryDto from dict
        user_entry = UserEntryDto(**user_entry_dict)
        print(f"📥 UserEntryDto reconstructed: {user_entry}")

        # Reconstruct LLMConfigDto from dict (if provided)
        llm_config = LLMConfigDto(**llm_config_dict) if llm_config_dict else None
        print(f"📥 LLMConfigDto reconstructed: {llm_config}")

        # Create course material generator V2 with LLM configuration
        generator = CourseMaterialGeneratorV2(
            db_session=db,
            embedding_model=embedding_model,
            llm_config=llm_config
        )

        # Generate course material
        result_v2 = generator.generate_course_material(
            user_entry=user_entry,
            top_k=top_k,
            category_quotas=None
        )

        # Construire le prompt complet
        full_prompt = (
            f"=== ÉTAPE 1: GÉNÉRATION DU JSON PÉDAGOGIQUE ===\n"
            f"{result_v2['prompts']['step1_pedagogical_json']}\n\n"
            f"=== ÉTAPE 2: MAPPING VERS TEMPLATES ===\n"
            f"{result_v2['prompts']['step2_template_structure']}"
        )

        # Extraire les informations de débogage
        debug_info = result_v2.get("debug_info", {})

        # Adapter le format de retour pour compatibilité avec le système existant
        result = {
            "success": True,
            "supports": result_v2["support"],  # Encapsuler dans une liste
            "templates_used": top_k,
            "prompt": full_prompt,
            "pedagogical_json": result_v2.get("pedagogical_json"),
            "destination_mappings": result_v2.get("destination_mappings"),
            "json_paths_with_variables": debug_info.get("json_paths_with_variables"),
            "path_groups": debug_info.get("path_groups"),
            "group_jsons_list": debug_info.get("group_jsons_list"),
            "group_jsons_map": debug_info.get("group_jsons_map"),
            "resolved_jsons_map": debug_info.get("resolved_jsons_map"),
            "path_to_value_map": debug_info.get("path_to_value_map"),
            "final_resolved_jsons_map": debug_info.get("final_resolved_jsons_map"),
        }

        print(f"📥 Course material generation V2 completed for task {task_id}")

        print(f" result = {json.dumps(result, indent=2, ensure_ascii=False)}")

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

        return result

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


@celery.task(name="generate.course_material_html")
def generate_course_material_html_task(
    task_id: str, user_entry_dict: dict, auth_uid: str, llm_config_dict: dict = None
):
    """
    Tâche Celery pour générer un support de cours HTML avec CourseMaterialGeneratorV3 et envoyer une notification FCM.

    Cette version utilise le nouveau générateur V3 qui:
    - Crée d'abord un JSON pédagogique enrichi avec explications complètes
    - Construit un mapping chemin → valeur à partir du JSON pédagogique
    - Groupe les chemins par préfixe
    - Génère du HTML pour chaque groupe en parallèle via LLM
    - Retourne des divs HTML avec CSS inline (pas de templates)

    Args:
        task_id: Identifiant unique de la tâche
        user_entry_dict: Dictionnaire UserEntryDto contenant le contexte, le contenu et les médias
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
        llm_config_dict: Dictionnaire LLMConfigDto optionnel pour la configuration des modèles LLM

    Returns:
        Dict contenant les supports HTML générés
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting course material HTML generation V3 for task {task_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Reconstruct UserEntryDto from dict
        user_entry = UserEntryDto(**user_entry_dict)
        print(f"📥 UserEntryDto reconstructed: {user_entry}")

        # Reconstruct LLMConfigDto from dict (if provided)
        llm_config = LLMConfigDto(**llm_config_dict) if llm_config_dict else None
        print(f"📥 LLMConfigDto reconstructed: {llm_config}")

        # Create course material generator V3 with LLM configuration
        generator = CourseMaterialGeneratorV3(
            db_session=db,
            embedding_model=embedding_model,
            llm_config=llm_config
        )

        # Generate course material HTML
        result_v3 = generator.generate_course_material(user_entry=user_entry)

        # Adapter le format de retour
        result = {
            "success": True,
            "html_supports": result_v3["htmlSupports"],
            "pedagogical_json": result_v3["pedagogical_json"],
            "debug_info": result_v3["debug_info"],
        }

        print(f"📥 Course material HTML generation V3 completed for task {task_id}")
        print(f" result = {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Publish result to Redis for WebSocket notifications
        redis.publish(
            "course_material_html_events",
            json.dumps(
                {
                    "event": "course_material_html_generated",
                    "type": "message",
                    "task_id": task_id,
                    "num_groups": result["debug_info"].get("num_groups", 0),
                    "num_paths": result["debug_info"].get("num_paths", 0),
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

                num_groups = result["debug_info"].get("num_groups", 0)

                # Send only metadata in FCM notification (Android has 4KB limit)
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Supports HTML générés",
                    body=f"{num_groups} groupe(s) de supports HTML ont été générés avec succès",
                    data={
                        "task_id": task_id,
                        "event": "course_material_html_generated",
                        "num_groups": str(num_groups),
                        # Don't send full data, app will fetch from API using task_id
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

        return result

    except Exception as e:
        print(f"❌ Error generating course material HTML for task {task_id}: {str(e)}")

        # Publish error to Redis
        redis.publish(
            "course_material_html_events",
            json.dumps(
                {"event": "course_material_html_error", "task_id": task_id, "error": str(e)}
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
                        body="Une erreur s'est produite lors de la génération des supports HTML",
                        data={
                            "task_id": task_id,
                            "event": "course_material_html_error",
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


@celery.task(name="modify.course_material_html")
def modify_course_material_html_task(
    task_id: str, modification_entry_dict: dict, auth_uid: str
):
    """
    Tâche Celery pour modifier un support de cours HTML existant selon des instructions libres.

    Args:
        task_id: Identifiant unique de la tâche
        modification_entry_dict: Dictionnaire CourseMaterialModificationEntryDto
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM
    """
    from app.models.dto.user_entry.course_material_modification_entry_dto import CourseMaterialModificationEntryDto

    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting course material HTML modification for task {task_id}")

    db = SessionLocal()

    try:
        entry = CourseMaterialModificationEntryDto(**modification_entry_dict)
        llm_config = entry.llm_config
        user_entry = entry.user_entry

        generator = CourseMaterialGeneratorV3(
            db_session=db,
            embedding_model=embedding_model,
            llm_config=llm_config,
        )

        result_v3 = generator.modify_course_material(
            pedagogical_json=entry.pedagogical_json,
            modification_instructions=entry.modification_instructions,
            user_entry=user_entry,
        )

        result = {
            "success": True,
            "html_supports": result_v3["htmlSupports"],
            "pedagogical_json": result_v3["pedagogical_json"],
            "debug_info": result_v3["debug_info"],
        }

        print(f"📥 Course material HTML modification completed for task {task_id}")

        redis.publish(
            "course_material_html_events",
            json.dumps({
                "event": "course_material_html_modified",
                "type": "message",
                "task_id": task_id,
            }),
        )

        user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
        if user:
            active_devices = (
                db.query(DeviceTokens)
                .filter(DeviceTokens.AppUserSKU == user.SKU, DeviceTokens.IsActive == True)
                .all()
            )
            if active_devices:
                fcm_service = FCMService()
                tokens = [device.FcmToken for device in active_devices]
                fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Support modifié",
                    body="Le support de cours a été modifié avec succès",
                    data={"task_id": task_id, "event": "course_material_html_modified"},
                    notification_id=task_id,
                )

        return result

    except Exception as e:
        print(f"❌ Error modifying course material HTML for task {task_id}: {str(e)}")

        redis.publish(
            "course_material_html_events",
            json.dumps({"event": "course_material_html_error", "task_id": task_id, "error": str(e)}),
        )

        try:
            user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
            if user:
                active_devices = (
                    db.query(DeviceTokens)
                    .filter(DeviceTokens.AppUserSKU == user.SKU, DeviceTokens.IsActive == True)
                    .all()
                )
                if active_devices:
                    fcm_service = FCMService()
                    tokens = [device.FcmToken for device in active_devices]
                    fcm_service.send_multicast_notification(
                        tokens=tokens,
                        title="Erreur de modification",
                        body="Une erreur s'est produite lors de la modification du support",
                        data={"task_id": task_id, "event": "course_material_html_error", "error": str(e)},
                        notification_id=task_id,
                    )
        except Exception as fcm_error:
            print(f"❌ Error sending FCM error notification: {str(fcm_error)}")

        raise

    finally:
        db.close()


@celery.task(name="generate.quiz")
def generate_quiz_task(
    task_id: str, request_dict: dict, auth_uid: str, llm_config_dict: dict = None
):
    """
    Tâche Celery pour générer un quiz à partir d'un JSON pédagogique.

    Deux modes :
    - Création (quiz_items is None) : génère N questions depuis le pedagogical_json
    - Modification (quiz_items fourni) : régénère chaque item en tenant compte du contenu existant
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"📥 Starting quiz generation for task {task_id}")
    print(f"📥 request_dict keys: {list(request_dict.keys())}")
    print(f"📥 llm_config_dict: {llm_config_dict}")
    print(f"📥 auth_uid: {auth_uid}")

    db = SessionLocal()

    try:
        print(f"🔧 Deserializing QuizGenerationRequestDto...")
        request = QuizGenerationRequestDto(**request_dict)
        print(f"🔧 Request deserialized — mode: {'modification' if request.quiz_items is not None else 'création'}, quiz_items count: {len(request.quiz_items) if request.quiz_items else 0}")
        print(f"🔧 courseName={request.courseName}, topicPath={request.topicPath}, additional_instructions={request.additional_instructions}")
        print(f"🔧 pedagogical_json keys: {list(request.pedagogical_json.keys()) if isinstance(request.pedagogical_json, dict) else type(request.pedagogical_json)}")

        llm_config = LLMConfigDto(**llm_config_dict) if llm_config_dict else LLMConfigDto()
        quiz_model = llm_config.get_quiz_model()
        print(f"🤖 Using LLM model: {quiz_model}")

        llm = create_universal_llm(quiz_model)
        print(f"🤖 LLM instance created: {type(llm).__name__}")

        pedagogical_json_str = json.dumps(request.pedagogical_json, ensure_ascii=False)
        course_context = ""
        if request.courseName:
            course_context += f"Cours : {request.courseName}\n"
        if request.topicPath:
            course_context += f"Topic : {request.topicPath}\n"
        if request.additional_instructions:
            course_context += f"Instructions supplémentaires : {request.additional_instructions}\n"

        is_creation_mode = request.quiz_items is None
        print(f"📝 Mode: {'création' if is_creation_mode else 'modification'}")

        if is_creation_mode:
            prompt = f"""Tu es un expert en pédagogie. Génère un quiz complet à partir du contenu pédagogique fourni.

{course_context}
JSON pédagogique :
{pedagogical_json_str}

Génère autant de questions que nécessaire pour couvrir les points clés du contenu.
Chaque question doit avoir entre 2 et 4 réponses possibles. Les réponses incorrectes doivent être plausibles et difficiles à distinguer de la bonne réponse.

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce format :
{{
  "quiz_items": [
    {{
      "questionJson": {{"type": "simpleText", "version": 1, "content": "TEXTE_DE_LA_QUESTION"}},
      "answersJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 1, "text": "RÉPONSE_1"}},
          {{"order": 2, "text": "RÉPONSE_2"}}
        ]
      }},
      "explanationJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 0, "text": "EXPLICATION_GÉNÉRALE"}},
          {{"order": 1, "text": "EXPLICATION_RÉPONSE_1"}},
          {{"order": 2, "text": "EXPLICATION_RÉPONSE_2"}}
        ]
      }},
      "correctAnswerOrder": 1
    }}
  ]
}}

Règles :
- correctAnswerOrder correspond à l'order de la bonne réponse dans answersJson.content
- explanationJson.content doit avoir order 0 (explication générale) + un order par réponse
- Les réponses incorrectes doivent être suffisamment proches de la bonne réponse pour rendre le choix difficile
- Ne génère que du JSON, aucun texte autour"""
        else:
            items_str = json.dumps(
                [item.model_dump() for item in request.quiz_items],
                ensure_ascii=False,
                indent=2
            )
            prompt = f"""Tu es un expert en pédagogie. Modifie et améliore les items de quiz fournis en te basant sur le JSON pédagogique.

{course_context}
JSON pédagogique :
{pedagogical_json_str}

Items de quiz existants à modifier :
{items_str}

Pour chaque item, régénère questionJson, answersJson, explanationJson et correctAnswerOrder.
Chaque question doit avoir entre 2 et 4 réponses possibles. Les réponses incorrectes doivent être plausibles et difficiles à distinguer de la bonne réponse.
Tiens compte du contenu existant des items et des instructions supplémentaires pour améliorer la qualité.

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce format (un item par item existant, dans le même ordre) :
{{
  "quiz_items": [
    {{
      "questionJson": {{"type": "simpleText", "version": 1, "content": "TEXTE_DE_LA_QUESTION"}},
      "answersJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 1, "text": "RÉPONSE_1"}},
          {{"order": 2, "text": "RÉPONSE_2"}}
        ]
      }},
      "explanationJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 0, "text": "EXPLICATION_GÉNÉRALE"}},
          {{"order": 1, "text": "EXPLICATION_RÉPONSE_1"}},
          {{"order": 2, "text": "EXPLICATION_RÉPONSE_2"}}
        ]
      }},
      "correctAnswerOrder": 1
    }}
  ]
}}

Règles :
- correctAnswerOrder correspond à l'order de la bonne réponse dans answersJson.content
- explanationJson.content doit avoir order 0 (explication générale) + un order par réponse
- Les réponses incorrectes doivent être suffisamment proches de la bonne réponse pour rendre le choix difficile
- Ne génère que du JSON, aucun texte autour"""

        print(f"📤 Sending prompt to LLM (model: {quiz_model}), prompt length: {len(prompt)} chars...")
        raw_response = llm.invoke(prompt)
        print(f"📩 Raw response type: {type(raw_response).__name__}, has 'content' attr: {hasattr(raw_response, 'content')}")
        response_text = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        print(f"📩 Raw response text (first 500 chars): {response_text[:500]}")

        response_text = response_text.strip()
        if response_text.startswith("```"):
            print(f"🧹 Stripping markdown code fences...")
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        print(f"🔍 Parsing JSON response (length: {len(response_text)} chars)...")
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON parse error: {json_err}")
            print(f"❌ Offending text (first 1000 chars): {response_text[:1000]}")
            raise

        raw_items = parsed.get("quiz_items", [])
        print(f"🔍 Parsed {len(raw_items)} quiz items from LLM response")

        quiz_items = []
        for i, item in enumerate(raw_items):
            print(f"🔧 Deserializing item {i}: keys={list(item.keys())}")
            try:
                quiz_items.append(QuizOutputItemDto(
                    questionJson=item["questionJson"],
                    answersJson=item["answersJson"],
                    explanationJson=item["explanationJson"],
                    correctAnswerOrder=item["correctAnswerOrder"],
                ))
            except Exception as item_err:
                print(f"❌ Failed to deserialize item {i}: {item_err}")
                print(f"❌ Item content: {json.dumps(item, ensure_ascii=False)}")
                raise

        quiz_items = [shuffle_quiz_item_answers(item) for item in quiz_items]
        print(f"🔀 Answers shuffled for all {len(quiz_items)} items")

        result = {
            "success": True,
            "quiz_items": [item.model_dump() for item in quiz_items],
        }

        print(f"✅ Quiz generation completed for task {task_id}: {len(quiz_items)} items")
        print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        redis.publish(
            "quiz_events",
            json.dumps({
                "event": "quiz_generated",
                "type": "message",
                "task_id": task_id,
                "num_items": len(quiz_items),
            }),
        )

        user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
        if user:
            active_devices = (
                db.query(DeviceTokens)
                .filter(DeviceTokens.AppUserSKU == user.SKU, DeviceTokens.IsActive == True)
                .all()
            )
            if active_devices:
                fcm_service = FCMService()
                tokens = [device.FcmToken for device in active_devices]
                fcm_result = fcm_service.send_multicast_notification(
                    tokens=tokens,
                    title="Quiz généré",
                    body=f"{len(quiz_items)} question(s) générée(s) avec succès",
                    data={
                        "task_id": task_id,
                        "event": "quiz_generation",
                        "num_items": str(len(quiz_items)),
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

        return result

    except Exception as e:
        import traceback
        print(f"❌ Error generating quiz for task {task_id}: {type(e).__name__}: {str(e)}")
        print(f"❌ Traceback:\n{traceback.format_exc()}")

        redis.publish(
            "quiz_events",
            json.dumps({"event": "quiz_error", "task_id": task_id, "error": str(e)}),
        )

        try:
            user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
            if user:
                active_devices = (
                    db.query(DeviceTokens)
                    .filter(DeviceTokens.AppUserSKU == user.SKU, DeviceTokens.IsActive == True)
                    .all()
                )
                if active_devices:
                    fcm_service = FCMService()
                    tokens = [device.FcmToken for device in active_devices]
                    fcm_service.send_multicast_notification(
                        tokens=tokens,
                        title="Erreur de génération",
                        body="Une erreur s'est produite lors de la génération du quiz",
                        data={
                            "task_id": task_id,
                            "event": "quiz_generation",
                            "error": str(e),
                        },
                        notification_id=task_id,
                    )
        except Exception as fcm_error:
            print(f"❌ Error sending FCM error notification: {str(fcm_error)}")

        raise

    finally:
        db.close()
