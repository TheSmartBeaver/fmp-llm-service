from pydantic import BaseModel, Field
from typing import Optional, Union, Literal

from app.chains.llm.llm_factory import LLMModel, LLMModelFactory
from app.models.dto.llm_config.all_llm_models import AllLLMModels


class LLMConfigDto(BaseModel):
    """
    Configuration des modèles LLM à utiliser pour les différentes étapes de génération.

    Permet de sélectionner un modèle spécifique (Anthropic, Google Gemini, OpenAI, Codex, O-series)
    pour chaque fonction clé du processus de génération de supports de cours.

    Supporte les modèles LangChain standard ainsi que les modèles OpenAI
    qui nécessitent l'endpoint /v1/responses via UniversalLLM.

    Usage:
        Utilisez l'enum AllLLMModels pour avoir l'auto-complétion de tous les modèles.
        Les valeurs string sont également acceptées pour la compatibilité.
    """

    pedagogical_json_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération du JSON pédagogique (_generate_pedagogical_json). Accepte AllLLMModels, LLMModel enum ou string"
    )

    pedagogical_json_mode: Optional[Literal["structured", "narrative"]] = Field(
        default="structured",
        description=(
            "Mode de génération du JSON pédagogique. "
            "'structured': découpe le contenu en sections thématiques (défaut). "
            "'narrative': génère un récit continu sous forme de segments ordonnés "
            "(narrative, aside, media), interrompus de remarques et explications."
        )
    )

    group_json_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération des JSONs de groupe (_generate_json_from_group_async). Accepte AllLLMModels, LLMModel enum ou string"
    )

    path_groups_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération des groupes de chemins (_generate_path_groups_with_llm). Accepte AllLLMModels, LLMModel enum ou string"
    )

    quiz_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération de quiz (quiz-from-plan + question HTML). Fallback sur pedagogical_json_model puis le modèle par défaut."
    )

    # ── Modèles par ÉTAPE des plans quiz/flashcards (chantier plans) ──────────
    # Chacun a un fallback sensé pour rester rétrocompatible.

    course_plan_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle pour la génération et la modification du PLAN DE COURS. Fallback : pedagogical_json_model."
    )

    assessment_plan_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle pour le PLAN GÉNÉRAL de quiz/flashcards. Fallback : pedagogical_json_model."
    )

    entity_plan_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle pour le PLAN DÉTAILLÉ d'une entité (question/carte). Fallback : assessment_plan_model."
    )

    flashcard_generation_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle pour la GÉNÉRATION des flashcards/cartes HTML. Fallback : quiz_model."
    )

    def _resolve(self, value) -> Optional[str]:
        """Normalise un champ modèle (AllLLMModels/str) en string, ou None."""
        if not value:
            return None
        if isinstance(value, AllLLMModels):
            return value.value
        return value

    def get_pedagogical_json_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Retourne le modèle pour la génération du JSON pédagogique (avec fallback sur défaut)"""
        if self.pedagogical_json_model:
            # Si c'est un AllLLMModels, retourner sa valeur string
            if isinstance(self.pedagogical_json_model, AllLLMModels):
                return self.pedagogical_json_model.value
            return self.pedagogical_json_model
        return LLMModelFactory.get_default_model()

    def get_group_json_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Retourne le modèle pour la génération des JSONs de groupe (avec fallback sur défaut)"""
        if self.group_json_model:
            if isinstance(self.group_json_model, AllLLMModels):
                return self.group_json_model.value
            return self.group_json_model
        return LLMModelFactory.get_default_model()

    def get_path_groups_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Retourne le modèle pour la génération des groupes de chemins (avec fallback sur défaut)"""
        if self.path_groups_model:
            if isinstance(self.path_groups_model, AllLLMModels):
                return self.path_groups_model.value
            return self.path_groups_model
        return LLMModelFactory.get_default_model()

    def get_quiz_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Modèle génération quiz (fallback sur pedagogical_json_model puis défaut)."""
        return self._resolve(self.quiz_model) or self.get_pedagogical_json_model()

    def get_course_plan_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Modèle du plan de cours (génération + modification). Fallback : pedagogical."""
        return self._resolve(self.course_plan_model) or self.get_pedagogical_json_model()

    def get_assessment_plan_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Modèle du plan général quiz/flashcards. Fallback : pedagogical."""
        return self._resolve(self.assessment_plan_model) or self.get_pedagogical_json_model()

    def get_entity_plan_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Modèle du plan détaillé d'entité. Fallback : plan général."""
        return self._resolve(self.entity_plan_model) or self.get_assessment_plan_model()

    def get_flashcard_generation_model(self) -> Union[AllLLMModels, LLMModel, str]:
        """Modèle de génération des cartes HTML. Fallback : modèle quiz."""
        return self._resolve(self.flashcard_generation_model) or self.get_quiz_model()

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "pedagogical_json_model": "gpt-5.2",
                    "group_json_model": "gemini-2.5-flash",
                    "path_groups_model": "claude-haiku-4-5-20251001"
                },
                {
                    "pedagogical_json_model": "o3-mini",
                    "group_json_model": "gpt-5-mini",
                    "path_groups_model": "claude-sonnet-4-5-20250929"
                },
                {
                    "pedagogical_json_model": "claude-sonnet-4-5-20250929",
                    "group_json_model": "gemini-3-flash-preview",
                    "path_groups_model": "gpt-5-mini"
                }
            ]
        }
