"""
Enum complet de TOUS les modèles LLM supportés par l'application.

Inclut:
- 34 modèles LangChain standard (via LLMModelFactory)
- 5 modèles Codex (via route /api/utils/codex)
- 5 modèles O-series (via route /api/utils/codex)

Total: 44 modèles disponibles avec une seule interface grâce à UniversalLLM.
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
    # OpenAI - GPT-5 Series (8 modèles)
    # ============================================================================
    GPT_5_2 = "gpt-5.2"
    GPT_5_1 = "gpt-5.1"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"
    GPT_5_2_CHAT_LATEST = "gpt-5.2-chat-latest"
    GPT_5_1_CHAT_LATEST = "gpt-5.1-chat-latest"
    GPT_5_CHAT_LATEST = "gpt-5-chat-latest"

    # ============================================================================
    # OpenAI - GPT-5 Codex (5 modèles) - Via UniversalLLM
    # ============================================================================
    GPT_5_1_CODEX_MAX = "gpt-5.1-codex-max"
    GPT_5_1_CODEX = "gpt-5.1-codex"
    GPT_5_CODEX = "gpt-5-codex"
    GPT_5_1_CODEX_MINI = "gpt-5.1-codex-mini"
    CODEX_MINI_LATEST = "codex-mini-latest"

    # ============================================================================
    # OpenAI - GPT-4 Series (6 modèles)
    # ============================================================================
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4O = "gpt-4o"
    GPT_4O_2024_05_13 = "gpt-4o-2024-05-13"
    GPT_4O_MINI = "gpt-4o-mini"

    # ============================================================================
    # OpenAI - Realtime Models (2 modèles)
    # ============================================================================
    GPT_REALTIME_MINI = "gpt-realtime-mini"
    GPT_4O_MINI_REALTIME_PREVIEW = "gpt-4o-mini-realtime-preview"

    # ============================================================================
    # OpenAI - O-Series / Reasoning Models (6 modèles)
    # ============================================================================
    O1_MINI = "o1-mini"  # LangChain compatible
    # Via UniversalLLM (route Codex):
    O3 = "o3"
    O3_MINI = "o3-mini"
    O3_DEEP_RESEARCH = "o3-deep-research"
    O4_MINI = "o4-mini"
    O4_MINI_DEEP_RESEARCH = "o4-mini-deep-research"

    # ============================================================================
    # OpenAI - Search Models (3 modèles)
    # ============================================================================
    GPT_5_SEARCH_API = "gpt-5-search-api"
    GPT_4O_MINI_SEARCH_PREVIEW = "gpt-4o-mini-search-preview"
    GPT_4O_SEARCH_PREVIEW = "gpt-4o-search-preview"

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
    # Anthropic - Claude 4 Series (3 modèles)
    # ============================================================================
    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_4_5_20250929 = "claude-sonnet-4-5-20250929"
    CLAUDE_OPUS_4_5 = "claude-opus-4-5"


# Modèles qui nécessitent la route Codex (pour référence)
CODEX_MODELS = {
    AllLLMModels.GPT_5_1_CODEX_MAX,
    AllLLMModels.GPT_5_1_CODEX,
    AllLLMModels.GPT_5_CODEX,
    AllLLMModels.GPT_5_1_CODEX_MINI,
    AllLLMModels.CODEX_MINI_LATEST,
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
