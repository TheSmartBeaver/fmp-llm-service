"""DTOs des plans d'évaluation (quiz / flashcards) et de leurs générations."""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from app.models.dto.llm_config.llm_config_dto import LLMConfigDto


class MediaAttachmentDto(BaseModel):
    """Fichier joint (audio, image, vidéo...) à intégrer dans l'entité générée."""
    url: str = Field(description='URL du média, préfixée "//media:"')
    description: Optional[str] = None
    media_type: Optional[str] = Field(
        default=None, description='Type de média : "image", "audio", "video", ...'
    )


class CardTemplateRefDto(BaseModel):
    """Référence légère d'une CardTemplate pour un PLAN (jamais le HTML complet)."""
    path: str
    fields_usage: Optional[str] = Field(
        default=None, description="TemplateFieldsUsage : mode d'emploi des champs du template"
    )


class CardTemplateFullDto(BaseModel):
    """CardTemplate complète, fournie uniquement à la GÉNÉRATION FINALE (transplantation)."""
    path: str
    template: str
    fields_usage: Optional[str] = None


class AssessmentPlanRequestDto(BaseModel):
    """Requête de plan général de quiz ou de flashcards."""
    kind: Literal["quiz", "flashcards"]
    pedagogical_json: dict
    course_plan_json: Optional[dict] = Field(
        default=None, description="Plan du cours, pour aligner le plan d'évaluation sur sa structure"
    )
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class EntityPlanRequestDto(BaseModel):
    """Requête de plan de construction d'UNE entité (question de quiz HTML ou flashcard full HTML)."""
    kind: Literal["quiz_question_html", "flashcard_full_html"]
    pedagogical_json: Optional[dict] = None
    source_block: Optional[dict] = Field(
        default=None, description="Bloc du plan général dont l'entité doit découler"
    )
    media: Optional[List[MediaAttachmentDto]] = Field(
        default=None, description="Fichiers joints à intégrer (question et/ou réponses)"
    )
    template_refs: Optional[List[CardTemplateRefDto]] = Field(
        default=None, description="Flashcards uniquement : templates référencés par {path, fields_usage}"
    )
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class QuizFromPlanRequestDto(BaseModel):
    """Génération directe de questions (mode texte) depuis les blocs ciblés du plan général."""
    plan_json: dict
    target_block_ids: List[str]
    pedagogical_json: dict
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class FlashcardsFromPlanRequestDto(BaseModel):
    """Génération directe de cartes full HTML depuis les blocs ciblés du plan général."""
    plan_json: dict
    target_block_ids: List[str]
    pedagogical_json: dict
    templates: Optional[List[CardTemplateFullDto]] = None
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class QuizQuestionHtmlRequestDto(BaseModel):
    """Génération finale d'une question riche depuis son plan d'entité."""
    plan_json: dict
    pedagogical_json: Optional[dict] = None
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class FlashcardHtmlRequestDto(BaseModel):
    """Génération finale d'une carte full HTML depuis son plan d'entité."""
    plan_json: dict
    templates: Optional[List[CardTemplateFullDto]] = Field(
        default=None, description="HTML complet des templates référencés par les blocs du plan"
    )
    pedagogical_json: Optional[dict] = None
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None
    llm_config: Optional[LLMConfigDto] = None


class AssessmentTaskResponse(BaseModel):
    """Réponse immédiate après lancement d'une tâche Celery."""
    task_id: str
    status: str = "pending"


class GeneratedCardDto(BaseModel):
    """Carte full HTML générée."""
    plan_block: Optional[str] = None
    full_html: str


class CardsHtmlResultResponse(BaseModel):
    """Résultat d'une génération de carte(s) full HTML."""
    success: bool
    cards: List[GeneratedCardDto]
    debug_info: Dict[str, Any] = Field(default_factory=dict)


class QuizQuestionHtmlResultResponse(BaseModel):
    """Résultat de la génération d'une question riche : JSON + HTML par slot."""
    success: bool
    question_json: dict
    answers_json: dict
    explanation_json: dict
    correct_answer_order: int
    slots: Dict[str, str] = Field(
        default_factory=dict,
        description='HTML par slot ("question", "answer_N", "explanation_N") pour les slots en rendering html',
    )
    debug_info: Dict[str, Any] = Field(default_factory=dict)
