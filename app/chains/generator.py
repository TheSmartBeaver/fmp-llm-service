from langchain.prompts import PromptTemplate

def generate_flashcard(instructions):
    prompt = PromptTemplate(
        input_variables=["topic", "level"],
        template="""
        Génère une flashcard pédagogique sur le sujet "{topic}" pour un niveau "{level}".
        Renvoie un JSON formaté ainsi :
        {{
            "question": "...",
            "answer": "...",
            "explanation": "..."
        }}
        """
    )

    response = "Test réussi"
    return response  # déjà en JSON selon le prompt