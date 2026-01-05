import os
from dotenv import find_dotenv, load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

class Gemini2_5_FlashLlm:
    chat: BaseChatModel

    def __init__(self):
        load_dotenv(find_dotenv())
        self.chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            timeout=100
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
