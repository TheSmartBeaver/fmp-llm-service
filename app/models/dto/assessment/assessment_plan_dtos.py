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


class CourseAssetDto(BaseModel):
    """
    Asset réutilisable du support de cours, extrait côté client par
    reconnaissance de forme du pedagogical_json.

    Deux natures :
      - type "image" : un fichier déjà lié au support, réutilisable tel quel.
        [filename] est le nom (avec extension) servi via "//media:".
      - type "anchor" : une section du support HTML identifiée par [anchor]
        ("#xxx"). Pour un PLAN, seul l'intitulé [heading] est fourni (le LLM
        choisit d'après le pedagogical_json). Pour la GÉNÉRATION FINALE, le
        fragment HTML de l'ancre est fourni dans [html_fragment] (extraction
        ciblée côté client, dans la limite de taille).
    """
    type: Literal["image", "anchor"]
    # image
    filename: Optional[str] = Field(default=None, description='Nom du fichier (avec extension) réutilisable via //media:')
    caption: Optional[str] = None
    # anchor
    anchor: Optional[str] = Field(default=None, description='Ancre HTML du support, ex "#petit-dejeuner"')
    heading: Optional[str] = None
    html_fragment: Optional[str] = Field(
        default=None,
        description="Génération finale uniquement : fragment HTML de l'ancre (extrait côté client, borné en taille)"
    )


class AssessmentPlanRequestDto(BaseModel):
    """Requête de plan général de quiz ou de flashcards."""
    kind: Literal["quiz", "flashcards"]
    pedagogical_json: dict
    course_plan_json: Optional[dict] = Field(
        default=None, description="Plan du cours, pour aligner le plan d'évaluation sur sa structure"
    )
    course_assets: Optional[List[CourseAssetDto]] = Field(
        default=None,
        description="Images et ancres réutilisables du support de cours (quiz uniquement)"
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
    course_assets: Optional[List[CourseAssetDto]] = Field(
        default=None,
        description="Question uniquement : images et ancres réutilisables du support de cours"
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
    course_assets: Optional[List[CourseAssetDto]] = Field(
        default=None,
        description="Images (réutilisables via //media:) et ancres AVEC leur html_fragment déjà extrait"
    )
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
    dropped_anchors: List[str] = Field(
        default_factory=list,
        description="Ancres du cours référencées mais ignorées (fragment introuvable ou trop volumineux)",
    )
    debug_info: Dict[str, Any] = Field(default_factory=dict)
