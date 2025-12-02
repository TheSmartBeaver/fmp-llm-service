from langchain_openai import ChatOpenAI

def run_simple_chain(message: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5
    )
    response = llm.invoke(message)
    return response.content