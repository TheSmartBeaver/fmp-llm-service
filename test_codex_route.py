"""
Script de test pour la route /api/utils/codex qui appelle GPT-5.1-codex.

Usage:
    python test_codex_route.py
"""

import httpx
import asyncio
import json


async def test_codex_route():
    """Teste la route codex avec différents exemples"""

    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/utils/codex"

    # Exemple 1: Génération de fonction Python
    print("=" * 60)
    print("Test 1: Génération de fonction Fibonacci")
    print("=" * 60)

    request_1 = {
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write clean, efficient code."
            },
            {
                "role": "user",
                "content": "Write a Python function to calculate the nth Fibonacci number using dynamic programming."
            }
        ],
        "model": "gpt-5.1-codex"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(endpoint, json=request_1)

        print(f"Status: {response.status_code}")
        result = response.json()

        if result["success"]:
            print(f"\n✅ Réponse de GPT-5.1-codex:\n")
            print(result["response"])
        else:
            print(f"\n❌ Erreur: {result['error']}")

    print("\n" + "=" * 60)
    print("Test 2: Refactoring de code")
    print("=" * 60)

    request_2 = {
        "messages": [
            {
                "role": "system",
                "content": "You are a code refactoring expert."
            },
            {
                "role": "user",
                "content": """Refactor this code to make it more readable and efficient:

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
    return result
"""
            }
        ],
        "model": "gpt-5.1-codex"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(endpoint, json=request_2)

        print(f"Status: {response.status_code}")
        result = response.json()

        if result["success"]:
            print(f"\n✅ Réponse de GPT-5.1-codex:\n")
            print(result["response"])
        else:
            print(f"\n❌ Erreur: {result['error']}")

    print("\n" + "=" * 60)
    print("Test 3: Génération de tests unitaires")
    print("=" * 60)

    request_3 = {
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in writing unit tests with pytest."
            },
            {
                "role": "user",
                "content": """Write pytest unit tests for this function:

def calculate_discount(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percentage / 100)
"""
            }
        ],
        "model": "gpt-5.1-codex"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(endpoint, json=request_3)

        print(f"Status: {response.status_code}")
        result = response.json()

        if result["success"]:
            print(f"\n✅ Réponse de GPT-5.1-codex:\n")
            print(result["response"])
        else:
            print(f"\n❌ Erreur: {result['error']}")

    print("\n" + "=" * 60)


async def test_with_curl_example():
    """Affiche un exemple de commande curl"""

    print("\n" + "=" * 60)
    print("Exemple de commande curl:")
    print("=" * 60)

    curl_command = """
curl -X POST "http://localhost:8000/api/utils/codex" \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a Python expert."
      },
      {
        "role": "user",
        "content": "Write a function to calculate fibonacci numbers"
      }
    ],
    "model": "gpt-5.1-codex",
    "temperature": 0.0,
    "max_tokens": 2048
  }'
"""

    print(curl_command)


if __name__ == "__main__":
    print("\n🚀 Test de la route /api/utils/codex avec GPT-5.1-codex\n")
    print("Assurez-vous que le serveur FastAPI est démarré (uvicorn app.main:app)")
    print("Et que OPENAI_API_KEY est configurée dans le fichier .env\n")

    asyncio.run(test_codex_route())
    asyncio.run(test_with_curl_example())

    print("\n✅ Tests terminés!\n")
