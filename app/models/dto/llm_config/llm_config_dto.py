from pydantic import BaseModel, Field
from typing import Optional

from app.chains.llm.llm_factory import LLMModel, LLMModelFactory


class LLMConfigDto(BaseModel):
    """
    Configuration des modèles LLM à utiliser pour les différentes étapes de génération.

    Permet de sélectionner un modèle spécifique (Anthropic, Google Gemini, OpenAI)
    pour chaque fonction clé du processus de génération de supports de cours.
    """

    pedagogical_json_model: Optional[LLMModel] = Field(
        default=None,
        description="Modèle LLM pour la génération du JSON pédagogique (_generate_pedagogical_json)"
    )

    group_json_model: Optional[LLMModel] = Field(
        default=None,
        description="Modèle LLM pour la génération des JSONs de groupe (_generate_json_from_group_async)"
    )

    path_groups_model: Optional[LLMModel] = Field(
        default=None,
        description="Modèle LLM pour la génération des groupes de chemins (_generate_path_groups_with_llm)"
    )

    def get_pedagogical_json_model(self) -> LLMModel:
        """Retourne le modèle pour la génération du JSON pédagogique (avec fallback sur défaut)"""
        return self.pedagogical_json_model or LLMModelFactory.get_default_model()

    def get_group_json_model(self) -> LLMModel:
        """Retourne le modèle pour la génération des JSONs de groupe (avec fallback sur défaut)"""
        return self.group_json_model or LLMModelFactory.get_default_model()

    def get_path_groups_model(self) -> LLMModel:
        """Retourne le modèle pour la génération des groupes de chemins (avec fallback sur défaut)"""
        return self.path_groups_model or LLMModelFactory.get_default_model()

    class Config:
        json_schema_extra = {
            "example": {
                "pedagogical_json_model": "gemini-2-5-flash",
                "group_json_model": "claude-haiku-4-5",
                "path_groups_model": "gpt-5-mini"
            }
        }
