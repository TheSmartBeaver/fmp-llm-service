from pydantic import BaseModel, Field
from typing import Optional, Union

from app.chains.llm.llm_factory import LLMModel, LLMModelFactory
from app.models.dto.llm_config.all_llm_models import AllLLMModels


class LLMConfigDto(BaseModel):
    """
    Configuration des modèles LLM à utiliser pour les différentes étapes de génération.

    Permet de sélectionner un modèle spécifique (Anthropic, Google Gemini, OpenAI, Codex, O-series)
    pour chaque fonction clé du processus de génération de supports de cours.

    ✨ Supporte TOUS les 44 modèles via UniversalLLM :
    - 34 modèles LangChain standard
    - 5 modèles Codex (gpt-5.1-codex, etc.)
    - 5 modèles O-series (o3, o3-mini, o4-mini, etc.)

    Usage:
        Utilisez l'enum AllLLMModels pour avoir l'auto-complétion de tous les modèles.
        Les valeurs string sont également acceptées pour la compatibilité.
    """

    pedagogical_json_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération du JSON pédagogique (_generate_pedagogical_json). Accepte AllLLMModels, LLMModel enum ou string"
    )

    group_json_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération des JSONs de groupe (_generate_json_from_group_async). Accepte AllLLMModels, LLMModel enum ou string"
    )

    path_groups_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération des groupes de chemins (_generate_path_groups_with_llm). Accepte AllLLMModels, LLMModel enum ou string"
    )

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

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "description": "Exemple avec modèles Codex et LangChain",
                    "value": {
                        "pedagogical_json_model": "gpt-5.1-codex",
                        "group_json_model": "gemini-2.5-flash",
                        "path_groups_model": "claude-haiku-4-5-20251001"
                    }
                },
                {
                    "description": "Exemple avec modèles O-series",
                    "value": {
                        "pedagogical_json_model": "o3-mini",
                        "group_json_model": "gpt-5-mini",
                        "path_groups_model": "claude-sonnet-4-5-20250929"
                    }
                }
            ]
        }
