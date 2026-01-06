"""
Exemple d'utilisation de GPT-5.1-codex via LangChain en utilisant la route /api/utils/codex.

Ce fichier montre comment intégrer la route Codex dans un workflow LangChain plus complexe.
"""

import httpx
import asyncio
from typing import List, Dict, Any


class CodexLangChainAdapter:
    """
    Adaptateur pour utiliser la route /api/utils/codex avec LangChain.

    Permet d'intégrer facilement GPT-5.1-codex dans des chains LangChain
    en passant par la route API personnalisée.
    """

    def __init__(self, base_url: str = "http://localhost:8000", model: str = "gpt-5.1-codex"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/utils/codex"
        self.model = model

    async def invoke(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Invoque GPT-5.1-codex avec les messages fournis.

        Args:
            messages: Liste de messages au format [{"role": "...", "content": "..."}]

        Returns:
            La réponse du modèle en tant que string

        Raises:
            Exception: Si l'appel échoue
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.endpoint,
                json={
                    "messages": messages,
                    "model": self.model
                }
            )

            result = response.json()

            if not result.get("success"):
                raise Exception(f"Codex API error: {result.get('error')}")

            return result.get("response", "")

    async def generate_code(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """
        Méthode helper pour générer du code avec un système prompt et user prompt.

        Args:
            system_prompt: Le prompt système (rôle du modèle)
            user_prompt: Le prompt utilisateur (demande)

        Returns:
            Le code généré
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return await self.invoke(messages)


# ============================================================================
# Exemples d'utilisation
# ============================================================================


async def example_1_simple_function():
    """Exemple 1: Génération simple de fonction"""
    print("=" * 60)
    print("Exemple 1: Génération de fonction simple")
    print("=" * 60)

    adapter = CodexLangChainAdapter()

    code = await adapter.generate_code(
        system_prompt="You are a Python expert. Write clean, documented code.",
        user_prompt="Write a function to check if a string is a palindrome"
    )

    print("\n✅ Code généré:\n")
    print(code)
    print("\n")


async def example_2_multi_turn():
    """Exemple 2: Conversation multi-tours pour itérer sur du code"""
    print("=" * 60)
    print("Exemple 2: Conversation multi-tours")
    print("=" * 60)

    adapter = CodexLangChainAdapter()

    # Tour 1: Génération initiale
    messages = [
        {
            "role": "system",
            "content": "You are a Python expert."
        },
        {
            "role": "user",
            "content": "Write a simple binary search function"
        }
    ]

    response_1 = await adapter.invoke(messages)
    print("\n📝 Tour 1 - Code initial:\n")
    print(response_1)

    # Tour 2: Amélioration
    messages.extend([
        {"role": "assistant", "content": response_1},
        {"role": "user", "content": "Now add type hints and docstring"}
    ])

    response_2 = await adapter.invoke(messages)
    print("\n📝 Tour 2 - Code amélioré:\n")
    print(response_2)

    # Tour 3: Tests
    messages.extend([
        {"role": "assistant", "content": response_2},
        {"role": "user", "content": "Now write pytest unit tests for this function"}
    ])

    response_3 = await adapter.invoke(messages)
    print("\n📝 Tour 3 - Tests unitaires:\n")
    print(response_3)
    print("\n")


async def example_3_langchain_workflow():
    """Exemple 3: Workflow LangChain complexe avec Codex"""
    print("=" * 60)
    print("Exemple 3: Workflow complexe type LangChain")
    print("=" * 60)

    adapter = CodexLangChainAdapter()

    # Étape 1: Analyser les besoins
    analysis_prompt = """
    I need to build a REST API endpoint that:
    - Accepts a list of numbers
    - Calculates statistics (mean, median, mode)
    - Returns results as JSON

    First, provide a high-level architecture for this endpoint.
    """

    architecture = await adapter.generate_code(
        system_prompt="You are a software architect.",
        user_prompt=analysis_prompt
    )

    print("\n📐 Architecture:\n")
    print(architecture)

    # Étape 2: Générer le code
    code_prompt = f"""
    Based on this architecture:

    {architecture}

    Now write the complete FastAPI endpoint implementation in Python.
    """

    implementation = await adapter.generate_code(
        system_prompt="You are a Python expert specializing in FastAPI.",
        user_prompt=code_prompt
    )

    print("\n💻 Implémentation:\n")
    print(implementation)

    # Étape 3: Générer les tests
    test_prompt = f"""
    For this FastAPI endpoint:

    {implementation}

    Write comprehensive pytest tests including edge cases.
    """

    tests = await adapter.generate_code(
        system_prompt="You are an expert in writing comprehensive test suites.",
        user_prompt=test_prompt
    )

    print("\n🧪 Tests:\n")
    print(tests)
    print("\n")


async def example_4_code_review():
    """Exemple 4: Revue de code automatique"""
    print("=" * 60)
    print("Exemple 4: Revue de code automatique")
    print("=" * 60)

    adapter = CodexLangChainAdapter()

    code_to_review = """
def process_users(users):
    result = []
    for user in users:
        if user['age'] > 18:
            if user['active'] == True:
                result.append({'name': user['name'], 'email': user['email']})
    return result
"""

    review = await adapter.generate_code(
        system_prompt="You are a senior code reviewer. Provide constructive feedback.",
        user_prompt=f"""Review this code and suggest improvements for:
- Readability
- Performance
- Pythonic style
- Error handling

Code:
{code_to_review}
"""
    )

    print("\n🔍 Revue de code:\n")
    print(review)
    print("\n")


async def example_5_multi_language():
    """Exemple 5: Conversion entre langages"""
    print("=" * 60)
    print("Exemple 5: Conversion Python → TypeScript")
    print("=" * 60)

    adapter = CodexLangChainAdapter()

    python_code = """
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    age: Optional[int] = None

def filter_adult_users(users: List[User]) -> List[User]:
    return [user for user in users if user.age and user.age >= 18]
"""

    typescript_code = await adapter.generate_code(
        system_prompt="You are an expert in Python and TypeScript.",
        user_prompt=f"""Convert this Python code to TypeScript with proper types:

{python_code}

Use TypeScript interfaces and maintain the same functionality.
"""
    )

    print("\n🔄 Code TypeScript:\n")
    print(typescript_code)
    print("\n")


async def main():
    """Exécute tous les exemples"""
    print("\n🚀 Exemples d'utilisation de GPT-5.1-codex avec LangChain\n")
    print("Assurez-vous que le serveur FastAPI est démarré!\n")

    try:
        await example_1_simple_function()
        await example_2_multi_turn()
        await example_3_langchain_workflow()
        await example_4_code_review()
        await example_5_multi_language()

        print("=" * 60)
        print("✅ Tous les exemples ont été exécutés avec succès!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous que:")
        print("1. Le serveur FastAPI est démarré (uvicorn app.main:app)")
        print("2. OPENAI_API_KEY est configurée dans .env")
        print("3. Vous avez accès aux modèles GPT-5.1-codex")


if __name__ == "__main__":
    asyncio.run(main())
