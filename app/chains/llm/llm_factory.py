from enum import Enum
from langchain_core.language_models.chat_models import BaseChatModel

from app.chains.llm.anthropic_llm import AnthropicLLM
from app.chains.llm.openai_llm import OpenAILLM
from app.chains.llm.google_llm import GoogleLLM
from app.chains.llm.openai_reasoning_llm import OpenAIReasoningLLM
# from app.chains.llm.openai_codex_llm import OpenAICodexLLM  # Non utilisé - modèles Codex désactivés


class LLMModel(str, Enum):
    """Enum des modèles LLM disponibles"""

    # ============ Google Gemini models ============
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"

    # ============ OpenAI models ============
    # GPT-5 series
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

    # GPT-5 Codex : routés via UniversalLLM et /v1/responses, donc non exposés ici.

    # GPT-4 series
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    # Search models
    GPT_5_SEARCH_API = "gpt-5-search-api"

    # ============ Anthropic Claude models ============
    # Claude 3 series
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"
    CLAUDE_3_5_HAIKU_20241022 = "claude-3-5-haiku-20241022"
    CLAUDE_HAIKU_4_5_20251001 = "claude-haiku-4-5-20251001"
    CLAUDE_3_SONNET_20240229 = "claude-3-sonnet-20240229"
    CLAUDE_3_5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
    CLAUDE_3_5_SONNET_20241022 = "claude-3-5-sonnet-20241022"
    CLAUDE_3_7_SONNET_20250219 = "claude-3-7-sonnet-20250219"

    # Claude 4 series
    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_4_5_20250929 = "claude-sonnet-4-5-20250929"
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"
    CLAUDE_OPUS_4_5 = "claude-opus-4-5"
    CLAUDE_OPUS_4_6 = "claude-opus-4-6"
    CLAUDE_OPUS_4_7 = "claude-opus-4-7"
    CLAUDE_OPUS_4_8 = "claude-opus-4-8"


class LLMModelFactory:
    """
    Factory pour créer des instances de LLM basées sur un enum.

    Utilise des classes génériques (AnthropicLLM, OpenAILLM, GoogleLLM) qui acceptent
    le nom du modèle directement, évitant la création d'une classe par modèle.
    """

    # Mapping des modèles vers leur provider
    _ANTHROPIC_MODELS = {
        LLMModel.CLAUDE_3_HAIKU_20240307,
        LLMModel.CLAUDE_3_5_HAIKU_20241022,
        LLMModel.CLAUDE_HAIKU_4_5_20251001,
        LLMModel.CLAUDE_3_SONNET_20240229,
        LLMModel.CLAUDE_3_5_SONNET_20240620,
        LLMModel.CLAUDE_3_5_SONNET_20241022,
        LLMModel.CLAUDE_3_7_SONNET_20250219,
        LLMModel.CLAUDE_SONNET_4_20250514,
        LLMModel.CLAUDE_SONNET_4_5_20250929,
        LLMModel.CLAUDE_SONNET_4_6,
        LLMModel.CLAUDE_OPUS_4_5,
        LLMModel.CLAUDE_OPUS_4_6,
        LLMModel.CLAUDE_OPUS_4_7,
        LLMModel.CLAUDE_OPUS_4_8,
    }

    _GOOGLE_MODELS = {
        LLMModel.GEMINI_2_5_FLASH_LITE,
        LLMModel.GEMINI_2_5_FLASH,
        LLMModel.GEMINI_3_FLASH_PREVIEW,
        LLMModel.GEMINI_2_0_FLASH,
        LLMModel.GEMINI_2_0_FLASH_LITE,
    }

    _OPENAI_REASONING_MODELS = set()

    # _OPENAI_CODEX_MODELS est désactivé car ces modèles ne sont pas compatibles
    # _OPENAI_CODEX_MODELS = {}

    # Tous les autres modèles sont OpenAI standard par défaut

    @staticmethod
    def get_llm(model: LLMModel) -> BaseChatModel:
        """
        Retourne une instance de LLM basée sur l'enum fourni.

        Args:
            model: Le modèle LLM à instancier (LLMModel enum)

        Returns:
            BaseChatModel: Instance du modèle LLM configuré

        Raises:
            ValueError: Si le modèle n'est pas supporté
        """
        # Déterminer le provider et créer l'instance appropriée
        if model in LLMModelFactory._ANTHROPIC_MODELS:
            return AnthropicLLM(model.value).get_llm()
        elif model in LLMModelFactory._GOOGLE_MODELS:
            return GoogleLLM(model.value).get_llm()
        elif model in LLMModelFactory._OPENAI_REASONING_MODELS:
            # Modèles de raisonnement OpenAI avec configuration spéciale
            return OpenAIReasoningLLM(model.value).get_llm()
        else:
            # Par défaut, OpenAI standard (pour tous les GPT, Search, Realtime, etc.)
            return OpenAILLM(model.value).get_llm()

    @staticmethod
    def get_default_model() -> LLMModel:
        """
        Retourne le modèle par défaut utilisé si aucun n'est spécifié.

        Returns:
            LLMModel: Le modèle par défaut (Gemini 2.5 Flash)
        """
        return LLMModel.CLAUDE_HAIKU_4_5_20251001
