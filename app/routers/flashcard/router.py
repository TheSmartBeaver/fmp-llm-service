import json
import os
import uuid
from celery.result import AsyncResult
from fastapi import APIRouter, Header, HTTPException
from redis import Redis
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.dto.assessment.assessment_plan_dtos import (
    AssessmentPlanRequestDto,
    AssessmentTaskResponse,
    CardsHtmlResultResponse,
    EntityPlanRequestDto,
    FlashcardHtmlRequestDto,
    FlashcardsFromPlanRequestDto,
)
from app.models.message import MessageRequest
from app.chains.simple_chain import run_simple_chain
from app.services.socket import socket_notify
from app.workers.celery_app import celery
from app.workers.tasks import (
    generate_flashcard_task,
    generate_assessment_plan_task,
    generate_entity_plan_task,
    generate_flashcards_from_plan_task,
    generate_flashcard_html_task,
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

flashcard_router = APIRouter(prefix="/flashcard_generation")


@flashcard_router.post("/generate_plan_CELERY", response_model=AssessmentTaskResponse)
async def generate_flashcards_plan(
    request: AssessmentPlanRequestDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Lance la génération asynchrone du PLAN GÉNÉRAL d'un jeu de flashcards
    (1 bloc = 1 carte esquissée) depuis le pedagogical_json du support de cours.

    Itération via POST /course_material/modify_plan_CELERY, résultat via
    GET /course_material/plan_result/{task_id}.
    """
    task_id = str(uuid.uuid4())
    request.kind = "flashcards"
    generate_assessment_plan_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid],
        task_id=task_id,
    )
    return AssessmentTaskResponse(task_id=task_id, status="pending")


@flashcard_router.post("/generate_card_plan_CELERY", response_model=AssessmentTaskResponse)
async def generate_flashcard_card_plan(
    request: EntityPlanRequestDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Lance la génération asynchrone du PLAN DE CONSTRUCTION d'UNE flashcard
    full HTML (convention <!--ANSWER_HIDDEN--> + classe fmp-hidden).

    Args:
        request: kind="flashcard_full_html" ; source_block optionnel (bloc du
            plan général) ; template_refs optionnels ({path, fields_usage}
            uniquement — le HTML complet des templates n'est fourni qu'à la
            génération finale) ; media optionnels.

    Résultat via GET /course_material/plan_result/{task_id}.
    """
    task_id = str(uuid.uuid4())
    request.kind = "flashcard_full_html"
    generate_entity_plan_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid],
        task_id=task_id,
    )
    return AssessmentTaskResponse(task_id=task_id, status="pending")


@flashcard_router.post("/generate_from_plan_CELERY", response_model=AssessmentTaskResponse)
async def generate_flashcards_from_plan(
    request: FlashcardsFromPlanRequestDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Génère les cartes full HTML des BLOCS CIBLÉS d'un plan général de
    flashcards. Chaque carte porte plan_block (l'ID du bloc dont elle découle).

    Résultat via GET /flashcard_generation/cards_html_result/{task_id}.
    """
    task_id = str(uuid.uuid4())
    generate_flashcards_from_plan_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid],
        task_id=task_id,
    )
    return AssessmentTaskResponse(task_id=task_id, status="pending")


@flashcard_router.post("/generate_card_html_CELERY", response_model=AssessmentTaskResponse)
async def generate_flashcard_card_html(
    request: FlashcardHtmlRequestDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Génération FINALE d'une carte full HTML depuis son plan d'entité validé.
    Les templates référencés par les blocs "template" du plan sont fournis ici
    en entier ({path, template, fields_usage}) et transplantés tels quels.

    Résultat via GET /flashcard_generation/cards_html_result/{task_id}.
    """
    task_id = str(uuid.uuid4())
    generate_flashcard_html_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid],
        task_id=task_id,
    )
    return AssessmentTaskResponse(task_id=task_id, status="pending")


@flashcard_router.get(
    "/cards_html_result/{task_id}",
    response_model=CardsHtmlResultResponse,
)
async def get_cards_html_result(task_id: str):
    """
    Récupère le résultat d'une génération de carte(s) full HTML
    (depuis un plan général ou un plan d'entité).

    Raises:
        HTTPException 202: tâche en cours ; 500: échec.
    """
    try:
        task_result = AsyncResult(task_id, app=celery)

        if task_result.state == "PENDING":
            raise HTTPException(
                status_code=202,
                detail={"status": "PENDING", "task_id": task_id,
                        "message": "La génération des cartes est en cours..."},
            )
        elif task_result.state == "SUCCESS":
            result = task_result.result
            return CardsHtmlResultResponse(
                success=result.get("success", True),
                cards=result.get("cards", []),
                debug_info=result.get("debug_info", {}),
            )
        elif task_result.state == "FAILURE":
            raise HTTPException(
                status_code=500,
                detail={"status": "FAILURE", "task_id": task_id,
                        "error": str(task_result.info)},
            )
        else:
            raise HTTPException(
                status_code=202,
                detail={"status": task_result.state, "task_id": task_id,
                        "message": f"État actuel: {task_result.state}"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du résultat: {str(e)}",
        )

@flashcard_router.post("/generate")
async def ask_bot(request: UserEntryDto):
    response = run_simple_chain(request)
    return {"response": response}

@flashcard_router.post("/generate_CELERY")
async def generate_flashcard(
    instructions: UserEntryDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid")
):
    """
    Lance une génération asynchrone de flashcard via Celery.

    Args:
        instructions: UserEntryDto contenant les instructions pour la génération
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM

    Returns:
        Dict avec l'ID de la tâche et le statut
    """
    task_id = str(uuid.uuid4())
    result = generate_flashcard_task.delay(task_id, instructions.model_dump(), auth_uid)
    # generate_flashcard_task(task_id+"aaaa", instructions)
    print("Job lancé ! ID:", result.id)

    # Récupérer le résultat (bloquant)
    # print("Résultat :", result.get())
    print("📥 Task queued with ID :", task_id)
    # fake
    # await socket_notify(
    #     event="flashcard_generated",
    #     data={"task_id": "fake_task_id", "flashcard": {"question": "Fake question", "answer": "Fake answer"}}
    # )
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis.publish("flashcard_events", json.dumps({
        "event": "flashcard_generated",
        "task_id": task_id,
        "flashcard": "DOGSHIT"
    }))

    return {"task_id": task_id, "status": "queued"}
