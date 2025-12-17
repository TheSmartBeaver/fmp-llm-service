import os
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

class OpenAiGPT5MiniLlm:
    chat: BaseChatModel

    def __init__(self):
        load_dotenv(find_dotenv())
        self.chat = ChatOpenAI(model_name="gpt-5-mini", name="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"), verbose=True, timeout=100)

    def get_llm(self) -> BaseChatModel:
        return self.chat
