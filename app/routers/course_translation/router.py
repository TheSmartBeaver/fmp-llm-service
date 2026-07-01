import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dto.course_translation.course_translation_dto import (
    CourseTranslationRequestDto,
    CourseTranslationResponseDto,
)
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.services.course_translation_service import (
    CourseTranslationError,
    CourseTranslationService,
)


logger = logging.getLogger(__name__)

course_translation_router = APIRouter(prefix="/courses", tags=["course-translation"])


@course_translation_router.post("/translate", response_model=CourseTranslationResponseDto)
async def translate_course(
    request: CourseTranslationRequestDto,
    llm_config: Optional[LLMConfigDto] = None,
    db: Session = Depends(get_db),
):
    """
    Clone un cours d'une langue vers une autre.

    - Si la traduction cible n'existe pas encore : clone complet du graphe du cours
      (Topics, CourseMaterials, HTML content, Quiz, Groups, flashcards, EasterEggs),
      avec traduction des textes légers (titres, description).
    - Si elle existe déjà : synchronisation (ajout des topics manquants, re-traduction
      des textes modifiés) sur la base des LastUpdated source vs cible.

    Ne sont PAS traduits (clonés bruts) : CourseMaterialHtmlContents, QuizQuestions,
    flashcards HtmlContents/Cards. Les FileContents (binaires) sont partagés entre langues.

    Args:
        request: course_code, source_language, target_language
        llm_config: configuration optionnelle du modèle LLM (utilise pedagogical_json_model)
        db: session de base de données

    Returns:
        CourseTranslationResponseDto avec le mode ('clone' ou 'sync') et les statistiques.
    """
    resolved_config = llm_config or LLMConfigDto()
    translation_model = resolved_config.get_pedagogical_json_model()

    service = CourseTranslationService(db=db, translation_model=translation_model)

    try:
        result = await service.translate_course(
            course_code=request.course_code,
            source_language=request.source_language,
            target_language=request.target_language,
        )
    except CourseTranslationError as e:
        db.rollback()
        logger.warning(
            "Traduction refusée (CourseCode=%s, %s -> %s) : %s: %s",
            request.course_code,
            request.source_language,
            request.target_language,
            type(e).__name__,
            e,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(
            "Erreur lors de la traduction du cours (CourseCode=%s, %s -> %s) : %s: %s",
            request.course_code,
            request.source_language,
            request.target_language,
            type(e).__name__,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la traduction du cours: {str(e)}",
        )

    return CourseTranslationResponseDto(
        message=(
            "Cours cloné dans la langue cible."
            if result["mode"] == "clone"
            else "Traduction existante synchronisée."
        ),
        **result,
    )
