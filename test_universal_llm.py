"""
Script de test pour UniversalLLM - wrapper qui supporte à la fois
les modèles LangChain standard et les modèles Codex/O-series.

Usage:
    python test_universal_llm.py
"""

import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.chains.llm.universal_llm import UniversalLLM, create_universal_llm
from app.chains.llm.llm_factory import LLMModel


async def test_langchain_model():
    """Test avec un modèle LangChain standard (Gemini)"""
    print("=" * 60)
    print("Test 1: Modèle LangChain standard (Gemini 2.5 Flash)")
    print("=" * 60)

    # Créer le LLM avec un modèle LangChain
    llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)

    # Test simple
    response = await llm.ainvoke("What is 2+2? Answer in one word.")
    print(f"\n✅ Réponse: {response}\n")

    return llm


async def test_codex_model():
    """Test avec un modèle Codex via la route dédiée"""
    print("=" * 60)
    print("Test 2: Modèle Codex (GPT-5.1-codex)")
    print("=" * 60)

    # Créer le LLM avec un modèle Codex (auto-détecté)
    llm = create_universal_llm("gpt-5.1-codex")

    # Test simple
    response = await llm.ainvoke("Write a one-line Python function to calculate factorial")
    print(f"\n✅ Réponse:\n{response}\n")

    return llm


async def test_with_langchain_chain():
    """Test avec une chaîne LangChain complète"""
    print("=" * 60)
    print("Test 3: UniversalLLM dans une chaîne LangChain")
    print("=" * 60)

    # Test avec Gemini
    print("\n📝 Avec Gemini 2.5 Flash:")
    llm_gemini = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{question}")
    ])

    chain = prompt | llm_gemini

    response = await chain.ainvoke({"question": "What is the capital of France? One word."})
    print(f"✅ Réponse: {response}")

    # Test avec Claude
    print("\n📝 Avec Claude Haiku 4.5:")
    llm_claude = create_universal_llm(LLMModel.CLAUDE_HAIKU_4_5_20251001)

    chain_claude = prompt | llm_claude
    response_claude = await chain_claude.ainvoke({"question": "What is 10 * 5? One word."})
    print(f"✅ Réponse: {response_claude}")

    # Test avec Codex
    print("\n📝 Avec GPT-5.1-codex:")
    llm_codex = create_universal_llm("gpt-5.1-codex")

    code_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Python expert. Write concise code."),
        ("user", "{request}")
    ])

    chain_codex = code_prompt | llm_codex
    response_codex = await chain_codex.ainvoke({
        "request": "Write a one-line lambda to square a number"
    })
    print(f"✅ Réponse:\n{response_codex}")


async def test_json_output_parser():
    """Test avec JsonOutputParser (cas d'usage réel de course_material_generator_v2)"""
    print("\n" + "=" * 60)
    print("Test 4: JsonOutputParser avec UniversalLLM")
    print("=" * 60)

    # Simuler le cas d'usage de pedagogical_json
    system_prompt = """You are a pedagogical content generator.
Generate a JSON object with the following structure:
{
    "title": "course title",
    "objective": "learning objective",
    "sections": [
        {"name": "section name", "content": "section content"}
    ]
}
"""

    user_prompt = "Create a short course about Python variables"

    # Test avec Gemini
    print("\n📝 Avec Gemini 2.5 Flash:")
    llm_gemini = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{topic}")
    ])

    chain = prompt | llm_gemini | JsonOutputParser()

    try:
        result = await chain.ainvoke({"topic": user_prompt})
        print(f"✅ JSON généré:")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"⚠️ Erreur de parsing JSON: {e}")
        print("(C'est normal, le modèle peut ne pas toujours retourner du JSON valide)")

    # Test avec Codex
    print("\n📝 Avec GPT-5.1-codex:")
    llm_codex = create_universal_llm("gpt-5.1-codex")

    code_gen_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a code generator. Return only valid JSON."),
        ("user", "Generate a JSON object with: function_name, parameters (array), and body (string) for a fibonacci function")
    ])

    chain_codex = code_gen_prompt | llm_codex | JsonOutputParser()

    try:
        result_codex = await chain_codex.ainvoke({})
        print(f"✅ JSON généré:")
        import json
        print(json.dumps(result_codex, indent=2))
    except Exception as e:
        print(f"⚠️ Erreur: {e}")


async def test_switching_models():
    """Test de changement de modèle à la volée"""
    print("\n" + "=" * 60)
    print("Test 5: Changer de modèle facilement")
    print("=" * 60)

    question = "What is the largest planet in our solar system? One word."

    models_to_test = [
        (LLMModel.GEMINI_2_5_FLASH, "Gemini 2.5 Flash"),
        (LLMModel.CLAUDE_HAIKU_4_5_20251001, "Claude Haiku 4.5"),
        (LLMModel.GPT_5_MINI, "GPT-5 Mini"),
        ("gpt-5.1-codex", "GPT-5.1-codex (Codex)"),
    ]

    for model_id, model_name in models_to_test:
        print(f"\n📝 Avec {model_name}:")
        try:
            llm = create_universal_llm(model_id)
            response = await llm.ainvoke(question)
            print(f"✅ Réponse: {response}")
        except Exception as e:
            print(f"❌ Erreur: {e}")


async def test_course_material_use_case():
    """Test simulant l'utilisation dans CourseMaterialGeneratorV2"""
    print("\n" + "=" * 60)
    print("Test 6: Simulation CourseMaterialGeneratorV2")
    print("=" * 60)

    # Simuler la génération de JSON pédagogique
    pedagogical_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a pedagogical expert. Generate educational content in JSON format.
Return a JSON object with:
- course: course name
- topic: main topic
- key_points: array of 3 key learning points
"""),
        ("user", "Topic: {topic}")
    ])

    # Tester avec différents modèles
    models = {
        "Gemini 2.5 Flash": LLMModel.GEMINI_2_5_FLASH,
        "Claude Haiku 4.5": LLMModel.CLAUDE_HAIKU_4_5_20251001,
        "GPT-5 Mini": LLMModel.GPT_5_MINI,
    }

    for model_name, model_enum in models.items():
        print(f"\n📚 Génération avec {model_name}:")
        try:
            llm = create_universal_llm(model_enum)
            chain = pedagogical_prompt | llm | JsonOutputParser()

            result = await chain.ainvoke({"topic": "Introduction to Machine Learning"})

            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ Erreur: {e}")


async def main():
    """Exécute tous les tests"""
    print("\n🚀 Tests de UniversalLLM - Wrapper universel pour LangChain et Codex\n")
    print("Assurez-vous que:")
    print("1. Le serveur FastAPI est démarré (uvicorn app.main:app)")
    print("2. OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY sont configurées\n")

    try:
        # Tests de base
        await test_langchain_model()
        await test_codex_model()

        # Tests avancés
        await test_with_langchain_chain()
        await test_json_output_parser()
        await test_switching_models()
        await test_course_material_use_case()

        print("\n" + "=" * 60)
        print("✅ Tous les tests terminés!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
