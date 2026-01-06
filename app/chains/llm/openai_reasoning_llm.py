import os
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel


class OpenAIReasoningLLM:
    """
    Classe spéciale pour les modèles de raisonnement OpenAI (O-series).

    Ces modèles (O1, O3, O4) utilisent une API différente avec des paramètres spéciaux :
    - Pas de system messages
    - Pas de temperature control
    - Pas de streaming
    - API endpoint différent (peut nécessiter des configurations spéciales)

    Note: Pour certains modèles O3/O4, OpenAI peut nécessiter l'utilisation de
    l'endpoint /v1/responses au lieu de /v1/chat/completions.
    """

    def __init__(self, model_name: str, timeout: int = 300):
        """
        Args:
            model_name: Le nom du modèle O-series (ex: "o3-mini", "o1-mini")
            timeout: Timeout en secondes (défaut: 300, car ces modèles sont plus lents)
        """
        load_dotenv(find_dotenv())

        # Configuration spéciale pour les modèles de raisonnement
        # Ces modèles ne supportent pas certains paramètres standard
        self.chat = ChatOpenAI(
            model_name=model_name,
            name=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=timeout,
            # Ne pas utiliser temperature pour les modèles O-series
            # Ne pas activer streaming
            streaming=False,
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
