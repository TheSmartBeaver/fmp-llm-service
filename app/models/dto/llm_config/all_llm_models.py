"""
Enum complet des modèles LLM supportés par l'application.

Regroupe les modèles standard routés via LangChain et les modèles OpenAI
spécifiques qui passent par l'endpoint /v1/responses via UniversalLLM.
"""

from enum import Enum


class AllLLMModels(str, Enum):
    """
    Enum complet de tous les modèles LLM supportés.

    Utilisez cet enum dans les routes FastAPI pour avoir l'auto-complétion
    et la validation de tous les modèles disponibles.

    Usage:
        ```python
        from app.models.dto.llm_config.all_llm_models import AllLLMModels

        class LLMConfigDto(BaseModel):
            pedagogical_json_model: Optional[AllLLMModels] = None
        ```
    """

    # ============================================================================
    # Google Gemini (5 modèles)
    # ============================================================================
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"

    # ============================================================================
    # OpenAI - GPT-5 Series
    # ============================================================================
    GPT_5_6_SOL = "gpt-5.6-sol"
    GPT_5_6_TERRA = "gpt-5.6-terra"
    GPT_5_6_LUNA = "gpt-5.6-luna"
    GPT_5_5 = "gpt-5.5"
    GPT_5_5_PRO = "gpt-5.5-pro"
    GPT_5_4 = "gpt-5.4"
    GPT_5_4_MINI = "gpt-5.4-mini"
    GPT_5_4_NANO = "gpt-5.4-nano"
    GPT_5_4_PRO = "gpt-5.4-pro"
    GPT_5_2 = "gpt-5.2"
    GPT_5_2_PRO = "gpt-5.2-pro"
    GPT_5_1 = "gpt-5.1"
    GPT_5 = "gpt-5"
    GPT_5_PRO = "gpt-5-pro"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"

    # ============================================================================
    # OpenAI - Codex via UniversalLLM (/v1/responses)
    # ============================================================================
    GPT_5_3_CODEX = "gpt-5.3-codex"

    # ============================================================================
    # OpenAI - GPT-4 Series
    # ============================================================================
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    # ============================================================================
    # OpenAI - O-Series / Reasoning Models via UniversalLLM
    # ============================================================================
    O1 = "o1"
    O1_PRO = "o1-pro"
    O3_PRO = "o3-pro"
    O3 = "o3"
    O3_MINI = "o3-mini"
    O3_DEEP_RESEARCH = "o3-deep-research"
    O4_MINI = "o4-mini"
    O4_MINI_DEEP_RESEARCH = "o4-mini-deep-research"

    # ============================================================================
    # OpenAI - Search Models
    # ============================================================================
    GPT_5_SEARCH_API = "gpt-5-search-api"

    # ============================================================================
    # Anthropic - Claude 3 Series (7 modèles)
    # ============================================================================
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"
    CLAUDE_3_5_HAIKU_20241022 = "claude-3-5-haiku-20241022"
    CLAUDE_HAIKU_4_5_20251001 = "claude-haiku-4-5-20251001"
    CLAUDE_3_SONNET_20240229 = "claude-3-sonnet-20240229"
    CLAUDE_3_5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
    CLAUDE_3_5_SONNET_20241022 = "claude-3-5-sonnet-20241022"
    CLAUDE_3_7_SONNET_20250219 = "claude-3-7-sonnet-20250219"

    # ============================================================================
    # Anthropic - Claude 4 Series (7 modèles)
    # ============================================================================
    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_4_5_20250929 = "claude-sonnet-4-5-20250929"
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"
    CLAUDE_OPUS_4_5 = "claude-opus-4-5"
    CLAUDE_OPUS_4_6 = "claude-opus-4-6"
    CLAUDE_OPUS_4_7 = "claude-opus-4-7"
    CLAUDE_OPUS_4_8 = "claude-opus-4-8"


# Modèles qui nécessitent la route Codex (pour référence)
CODEX_MODELS = {
    AllLLMModels.O1,
    AllLLMModels.O1_PRO,
    AllLLMModels.O3_PRO,
    AllLLMModels.GPT_5_3_CODEX,
    AllLLMModels.O3,
    AllLLMModels.O3_MINI,
    AllLLMModels.O3_DEEP_RESEARCH,
    AllLLMModels.O4_MINI,
    AllLLMModels.O4_MINI_DEEP_RESEARCH,
}


def is_codex_model(model: AllLLMModels) -> bool:
    """
    Vérifie si un modèle nécessite la route Codex.

    Args:
        model: Le modèle à vérifier

    Returns:
        True si le modèle nécessite la route Codex, False sinon
    """
    return model in CODEX_MODELS
