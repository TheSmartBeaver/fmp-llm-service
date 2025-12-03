from langchain_openai import ChatOpenAI

from app.chains.llm.open_ai_gpt4o_mini_llm import OpenAiGPT4oMiniLlm
from app.chains.prompt_templates.generation_prompt import FC_GENERATION_PROMPT
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

openAiGPT4oMiniLlm = OpenAiGPT4oMiniLlm().get_llm()

def run_simple_chain(userEntryDto: UserEntryDto) -> str:

    messages = []

    messages.append(
        AIMessagePromptTemplate.from_template(FC_GENERATION_PROMPT)
    )

    finalPrompt = ChatPromptTemplate(
        input_variables=["job_desc", "estimate", "skills_compatibility", "previous_guess"], messages=messages
    )

    chain = LLMChain(llm=openAiGPT4oMiniLlm, prompt=finalPrompt, verbose=True)

    promptArgs = {
        "topic": userEntryDto.context_entry.course
    }

    result = chain.run(promptArgs)

    return result