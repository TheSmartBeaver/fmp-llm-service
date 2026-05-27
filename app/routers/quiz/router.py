from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import uuid
import json
from celery.result import AsyncResult

from app.models.dto.quiz.quiz_dto import (
    QuizGenerationRequestDto,
    QuizOutputItemDto,
    QuizResultResponse,
    QuizTaskResponse,
)
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.workers.tasks import generate_quiz_task
from app.workers.celery_app import celery
from app.chains.llm.universal_llm import create_universal_llm


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


@quiz_router.post("/generate_sync", response_model=QuizResultResponse)
async def generate_quiz_sync(
    request: QuizGenerationRequestDto,
    llm_config: Optional[LLMConfigDto] = None,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
):
    """
    Génère un quiz de façon synchrone et retourne directement le résultat.

    Deux modes selon la valeur de quiz_items :
    - Création (quiz_items absent ou null) : génère un quiz complet depuis pedagogical_json
    - Modification (quiz_items fourni) : régénère chaque item en tenant compte du contenu existant

    Args:
        request: Corps de la requête contenant pedagogical_json, quiz_items optionnel,
                 additional_instructions, courseName et topicPath
        llm_config: Configuration optionnelle des modèles LLM (utilise quiz_model en priorité)
        auth_uid: AuthentUid de l'utilisateur (non utilisé en synchrone, conservé pour cohérence)

    Returns:
        QuizResultResponse avec la liste des items de quiz générés
    """
    try:
        resolved_llm_config = llm_config or LLMConfigDto()
        quiz_model = resolved_llm_config.get_quiz_model()
        llm = create_universal_llm(quiz_model)

        pedagogical_json_str = json.dumps(request.pedagogical_json, ensure_ascii=False)
        course_context = ""
        if request.courseName:
            course_context += f"Cours : {request.courseName}\n"
        if request.topicPath:
            course_context += f"Topic : {request.topicPath}\n"
        if request.additional_instructions:
            course_context += f"Instructions supplémentaires : {request.additional_instructions}\n"

        is_creation_mode = request.quiz_items is None

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
                indent=2,
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

        raw_response = llm.invoke(prompt)
        response_text = raw_response.content if hasattr(raw_response, "content") else str(raw_response)

        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        parsed = json.loads(response_text)
        raw_items = parsed.get("quiz_items", [])

        quiz_items = [
            QuizOutputItemDto(
                questionJson=item["questionJson"],
                answersJson=item["answersJson"],
                explanationJson=item["explanationJson"],
                correctAnswerOrder=item["correctAnswerOrder"],
            )
            for item in raw_items
        ]

        return QuizResultResponse(success=True, quiz_items=quiz_items)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du quiz: {str(e)}",
        )


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
