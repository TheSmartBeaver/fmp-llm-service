import os
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel


class OpenAILLM:
    """
    Classe générique pour créer des instances ChatOpenAI avec n'importe quel modèle.
    """

    def __init__(self, model_name: str, timeout: int = 100, verbose: bool = True):
        """
        Args:
            model_name: Le nom du modèle OpenAI (ex: "gpt-5-mini")
            timeout: Timeout en secondes (défaut: 100)
            verbose: Mode verbose (défaut: True)
        """
        load_dotenv(find_dotenv())
        self.chat = ChatOpenAI(
            model_name=model_name,
            name=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            verbose=verbose,
            timeout=timeout
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
