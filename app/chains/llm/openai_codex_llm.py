import os
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel


class OpenAICodexLLM:
    """
    Classe spéciale pour les modèles Codex d'OpenAI.

    Les modèles Codex sont optimisés pour la génération et compréhension de code.
    Ils peuvent avoir des exigences API différentes des modèles GPT standards.

    Note: Certains modèles Codex peuvent nécessiter des configurations spéciales
    ou des endpoints différents selon la version de l'API OpenAI.
    """

    def __init__(self, model_name: str, timeout: int = 120, temperature: float = 0.0):
        """
        Args:
            model_name: Le nom du modèle Codex (ex: "gpt-5.1-codex-mini")
            timeout: Timeout en secondes (défaut: 120)
            temperature: Temperature pour la génération (défaut: 0.0 pour le code)
        """
        load_dotenv(find_dotenv())

        # Configuration pour les modèles Codex
        # Temperature basse par défaut pour la génération de code
        self.chat = ChatOpenAI(
            model_name=model_name,
            name=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=timeout,
            temperature=temperature,
            # Codex fonctionne mieux avec ces paramètres
            max_tokens=2048,
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
