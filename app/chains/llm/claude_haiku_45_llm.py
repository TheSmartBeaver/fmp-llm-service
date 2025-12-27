import os
from dotenv import find_dotenv, load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

class ClaudeHaiku45Llm:
    chat: BaseChatModel

    def __init__(self):
        load_dotenv(find_dotenv())
        self.chat = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=8192,
            timeout=100
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
