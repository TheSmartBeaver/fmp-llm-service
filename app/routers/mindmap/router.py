from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import Any, Dict, List
from celery.result import AsyncResult
import uuid

from app.database import get_db
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.mind_map_generator import MindMapGenerator
from app.workers.tasks import generate_mindmap_task, generate_flashcard_from_pedag_task
from app.workers.celery_app import celery
from app.models.dto.user_entry.context_entry_dto import ContextEntryDto
from app.models.dto.user_entry.pedagogical_context_entry_dto import PedagogicalContextEntryDto


mindmap_router = APIRouter(prefix="/mindmap")

# Charger le modèle d'embedding UNE SEULE FOIS (important pour les performances)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)

# Charger le LLM OpenAI
openai_llm = OpenAiGPT5MiniLlm().get_llm()


class MindMapRequest(BaseModel):
    """Requête pour générer une carte mentale"""
    raw_data: str
    top_k: int = 15

    class Config:
        json_schema_extra = {
            "example": {
                "raw_data": "La photosynthèse est le processus par lequel les plantes vertes utilisent la lumière du soleil pour synthétiser des nutriments à partir de dioxyde de carbone et d'eau. Elle génère de l'oxygène comme sous-produit.",
                "top_k": 15
            }
        }


class MindMapResponse(BaseModel):
    """Réponse contenant la carte mentale générée"""
    success: bool
    mind_map: Dict[str, Any]
    templates_used: int
    prompt: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "mind_map": {
                    "recto": {
                        "template_name": "question_template",
                        "field_name_1": "Qu'est-ce que la photosynthèse?"
                    },
                    "verso": {
                        "template_name": "answer_template",
                        "field_name_1": "Un processus de conversion d'énergie lumineuse"
                    },
                    "version": "1.0.0"
                },
                "templates_used": 15,
                "prompt": "Voici les informations pédagogiques brutes..."
            }
        }


class MindMapTaskResponse(BaseModel):
    """Réponse contenant l'ID de la tâche Celery"""
    task_id: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending"
            }
        }


@mindmap_router.post("/generate/async", response_model=MindMapTaskResponse)
async def generate_mindmap_async(
    request: MindMapRequest
):
    """
    Lance une génération asynchrone de carte mentale via Celery.

    Args:
        request: Contient raw_data (données brutes) et top_k (nombre de templates à utiliser)

    Returns:
        MindMapTaskResponse avec l'ID de la tâche Celery

    Note:
        Le résultat sera publié sur Redis (canal 'mindmap_events') une fois la génération terminée.
    """
    # Générer un ID unique pour cette tâche
    task_id = str(uuid.uuid4())

    # Lancer la tâche Celery de manière asynchrone
    generate_mindmap_task.apply_async(
        args=[task_id, request.raw_data, request.top_k],
        task_id=task_id
    )

    return MindMapTaskResponse(
        task_id=task_id,
        status="pending"
    )


@mindmap_router.post("/generate", response_model=MindMapResponse)
async def generate_mindmap(
    request: MindMapRequest,
    db: Session = Depends(get_db)
):
    """
    Génère une carte mentale à partir de données pédagogiques brutes (mode synchrone).

    Args:
        request: Contient raw_data (données brutes) et top_k (nombre de templates à utiliser)
        db: Session de base de données (injectée automatiquement)

    Returns:
        MindMapResponse avec le JSON de la carte mentale générée

    Raises:
        HTTPException: En cas d'erreur de génération ou de validation

    Note:
        Pour une exécution asynchrone, utilisez /generate/async
    """
    try:
        # Créer le générateur
        generator = MindMapGenerator(
            db_session=db,
            llm=openai_llm,
            embedding_model=embedding_model
        )

        # Générer la carte mentale
        result = generator.generate_mind_map(
            raw_data=request.raw_data,
            top_k=request.top_k
        )

        return MindMapResponse(
            success=True,
            mind_map=result["mind_map"],
            templates_used=request.top_k,
            prompt=result["prompt"]
        )

    except ValueError as e:
        # Erreur de validation du JSON
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de validation: {str(e)}"
        )

    except Exception as e:
        # Erreur inattendue
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


class FlashcardFromPedagRequest(BaseModel):
    """Requête pour générer des flashcards à partir d'un JSON pédagogique"""
    context: ContextEntryDto
    pedagogical_json: str
    top_k: int = 12

    class Config:
        json_schema_extra = {
            "example": {
                "context": {
                    "course": "Biologie",
                    "topic_path": "Cellule/Photosynthèse",
                    "fc_to_modify": ""
                },
                "pedagogical_json": '{"title": "La photosynthèse", "content": "Processus de conversion..."}',
                "top_k": 15
            }
        }


class FlashcardFromPedagResponse(BaseModel):
    """Réponse contenant les flashcards générées à partir d'un JSON pédagogique"""
    success: bool
    mind_map: List[Dict[str, Any]]
    templates_used: int
    prompt: str


@mindmap_router.post("/generate_flashcard_from_pedag_async", response_model=MindMapTaskResponse)
async def generate_flashcard_from_pedag_async(
    request: FlashcardFromPedagRequest,
    auth_uid: str = Header(..., alias="X-Auth-Uid")
):
    """
    Lance une génération asynchrone de flashcards à partir d'un JSON pédagogique via Celery.

    Args:
        request: Contient context (ContextEntryDto), pedagogical_json (string JSON) et top_k
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM

    Returns:
        MindMapTaskResponse avec l'ID de la tâche Celery

    Note:
        Une notification FCM sera envoyée une fois la génération terminée.
        Le résultat peut être récupéré via le task_id.
    """
    # Générer un ID unique pour cette tâche
    task_id = str(uuid.uuid4())

    # Construire le DTO pour la tâche Celery
    pedag_entry = PedagogicalContextEntryDto(
        context=request.context,
        pedagogical_json=request.pedagogical_json
    )

    # Lancer la tâche Celery de manière asynchrone
    generate_flashcard_from_pedag_task.apply_async(
        args=[task_id, pedag_entry.model_dump(), auth_uid, request.top_k],
        task_id=task_id
    )

    return MindMapTaskResponse(
        task_id=task_id,
        status="pending"
    )


@mindmap_router.get("/flashcard_from_pedag/{task_id}", response_model=FlashcardFromPedagResponse)
async def get_flashcard_from_pedag_result(task_id: str):
    """
    Récupère le résultat d'une tâche de génération de flashcards via son task_id.

    Args:
        task_id: ID unique de la tâche Celery

    Returns:
        FlashcardFromPedagResponse avec les flashcards générées

    Raises:
        HTTPException 202: Si la tâche est en cours (PENDING)
        HTTPException 500: Si la tâche a échoué (FAILURE) ou erreur interne
    """
    try:
        task_result = AsyncResult(task_id, app=celery)

        print(f"🔍 Task {task_id} - State: {task_result.state}")
        print(f"🔍 Task {task_id} - Ready: {task_result.ready()}")
        print(f"🔍 Task {task_id} - Successful: {task_result.successful() if task_result.ready() else 'N/A'}")

        if task_result.state == "PENDING":
            raise HTTPException(
                status_code=202,
                detail={
                    "status": "PENDING",
                    "task_id": task_id,
                    "message": "La génération est en cours..."
                }
            )

        elif task_result.state == "SUCCESS":
            result = task_result.result

            return FlashcardFromPedagResponse(
                success=result.get("success", True),
                mind_map=result.get("mind_map", []),
                templates_used=result.get("templates_used", 0),
                prompt=result.get("prompt", "")
            )

        elif task_result.state == "FAILURE":
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "FAILURE",
                    "task_id": task_id,
                    "error": str(task_result.info)
                }
            )

        else:
            raise HTTPException(
                status_code=202,
                detail={
                    "status": task_result.state,
                    "task_id": task_id,
                    "message": f"État actuel: {task_result.state}"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du résultat: {str(e)}"
        )


@mindmap_router.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel.
    """
    return {
        "status": "ok",
        "service": "mindmap_generator",
        "embedding_model": MODEL_NAME,
        "llm_model": "gpt-5-mini"
    }
