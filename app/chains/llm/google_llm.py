import os
from dotenv import find_dotenv, load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel


class GoogleLLM:
    """
    Classe générique pour créer des instances ChatGoogleGenerativeAI avec n'importe quel modèle.
    """

    def __init__(self, model_name: str, temperature: float = 0.7, timeout: int = 100):
        """
        Args:
            model_name: Le nom du modèle Google (ex: "gemini-2.5-flash")
            temperature: Température pour la génération (défaut: 0.7)
            timeout: Timeout en secondes (défaut: 100)
        """
        load_dotenv(find_dotenv())
        self.chat = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=temperature,
            timeout=timeout
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
