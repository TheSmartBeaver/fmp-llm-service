import os
from dotenv import find_dotenv, load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel


class AnthropicLLM:
    """
    Classe générique pour créer des instances ChatAnthropic avec n'importe quel modèle.
    """

    def __init__(self, model_name: str, max_tokens: int = 8192, timeout: int = 100):
        """
        Args:
            model_name: Le nom du modèle Anthropic (ex: "claude-haiku-4-5-20251001")
            max_tokens: Nombre maximum de tokens (défaut: 8192)
            timeout: Timeout en secondes (défaut: 100)
        """
        load_dotenv(find_dotenv())
        self.chat = ChatAnthropic(
            model=model_name,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=max_tokens,
            timeout=timeout
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
