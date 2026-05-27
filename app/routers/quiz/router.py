from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import uuid
from celery.result import AsyncResult

from app.models.dto.quiz.quiz_dto import (
    QuizGenerationRequestDto,
    QuizResultResponse,
    QuizTaskResponse,
)
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.workers.tasks import generate_quiz_task
from app.workers.celery_app import celery


quiz_router = APIRouter(prefix="/quiz")


@quiz_router.post("/generate", response_model=QuizTaskResponse)
async def generate_quiz(
    request: QuizGenerationRequestDto,
    llm_config: Optional[LLMConfigDto] = None,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Lance une génération asynchrone de quiz via Celery.

    Deux modes selon la valeur de quiz_items :
    - Création (quiz_items absent ou null) : génère un quiz complet depuis pedagogical_json
    - Modification (quiz_items fourni) : régénère chaque item en tenant compte du contenu existant

    Args:
        request: Corps de la requête contenant pedagogical_json, quiz_items optionnel,
                 additional_instructions, courseName et topicPath
        llm_config: Configuration optionnelle des modèles LLM (utilise quiz_model en priorité)
        auth_uid: AuthentUid de l'utilisateur pour les notifications FCM

    Returns:
        QuizTaskResponse avec l'ID de la tâche Celery

    Note:
        Une notification FCM sera envoyée aux appareils actifs une fois la génération terminée.
        Utilisez GET /quiz/result/{task_id} pour récupérer le résultat.
    """
    task_id = str(uuid.uuid4())

    llm_config_dict = llm_config.model_dump() if llm_config else None

    generate_quiz_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid, llm_config_dict],
        task_id=task_id,
    )

    return QuizTaskResponse(task_id=task_id, status="pending")


@quiz_router.get("/result/{task_id}", response_model=QuizResultResponse)
async def get_quiz_result(task_id: str):
    """
    Récupère le résultat d'une tâche de génération de quiz via son task_id.

    Args:
        task_id: ID unique de la tâche Celery

    Returns:
        QuizResultResponse avec la liste des items de quiz générés

    Raises:
        HTTPException 202: Si la tâche est en cours (PENDING ou STARTED)
        HTTPException 500: Si la tâche a échoué (FAILURE) ou erreur interne
    """
    try:
        task_result = AsyncResult(task_id, app=celery)

        print(f"🔍 Quiz task {task_id} - State: {task_result.state}")

        if task_result.state == "PENDING":
            raise HTTPException(
                status_code=202,
                detail={
                    "status": "PENDING",
                    "task_id": task_id,
                    "message": "La génération du quiz est en cours...",
                },
            )

        elif task_result.state == "SUCCESS":
            result = task_result.result
            return QuizResultResponse(
                success=result.get("success", True),
                quiz_items=result.get("quiz_items", []),
            )

        elif task_result.state == "FAILURE":
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "FAILURE",
                    "task_id": task_id,
                    "error": str(task_result.info),
                },
            )

        else:
            raise HTTPException(
                status_code=202,
                detail={
                    "status": task_result.state,
                    "task_id": task_id,
                    "message": f"État actuel: {task_result.state}",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du résultat: {str(e)}",
        )
