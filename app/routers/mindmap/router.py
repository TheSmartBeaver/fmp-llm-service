from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import Any, Dict
import uuid

from app.database import get_db
from app.chains.llm.open_ai_gpt52_llm import OpenAiGPT52Llm
from app.chains.mind_map_generator import MindMapGenerator
from app.workers.tasks import generate_mindmap_task


mindmap_router = APIRouter(prefix="/mindmap")

# Charger le modèle d'embedding UNE SEULE FOIS (important pour les performances)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)

# Charger le LLM OpenAI
openai_llm = OpenAiGPT52Llm().get_llm()


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

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "mind_map": {
                    "recto": {
                        "template_name": "question_template",
                        "field1": "Qu'est-ce que la photosynthèse?"
                    },
                    "verso": {
                        "template_name": "answer_template",
                        "field1": "Un processus de conversion d'énergie lumineuse"
                    },
                    "version": "1.0.0"
                },
                "templates_used": 15
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
        mind_map = generator.generate_mind_map(
            raw_data=request.raw_data,
            top_k=request.top_k
        )

        return MindMapResponse(
            success=True,
            mind_map=mind_map,
            templates_used=request.top_k
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


@mindmap_router.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel.
    """
    return {
        "status": "ok",
        "service": "mindmap_generator",
        "embedding_model": MODEL_NAME,
        "llm_model": "gpt-5.2"
    }
