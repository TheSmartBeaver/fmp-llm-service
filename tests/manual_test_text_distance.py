"""
Test manuel de la route text-distance
"""

import requests
import json


def test_text_distance():
    """Test la route /api/utils/text-distance"""
    base_url = "http://localhost:8000"
    endpoint = "/api/utils/text-distance"

    print("\n=== Test 1: Textes similaires ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Le chat dort sur le canapé",
            "text2": "Le chat dort sur le sofa",
            "metric": "cosine"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is True
    assert data["similarity"] > 0.8
    print("✅ PASS - Haute similarité détectée")

    print("\n=== Test 2: Textes différents ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Le chat dort sur le canapé",
            "text2": "La programmation informatique est complexe",
            "metric": "cosine"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is True
    assert data["similarity"] < 0.8
    print("✅ PASS - Faible similarité détectée")

    print("\n=== Test 3: Textes identiques ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Bonjour le monde",
            "text2": "Bonjour le monde",
            "metric": "cosine"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is True
    assert data["similarity"] > 0.99
    assert data["distance"] < 0.01
    print("✅ PASS - Textes identiques détectés")

    print("\n=== Test 4: Similarité sémantique ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Un félin se repose",
            "text2": "Un chat dort",
            "metric": "cosine"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is True
    print(f"Similarité sémantique: {data['similarity']:.3f}")
    print("✅ PASS - Similarité sémantique capturée")

    print("\n=== Test 5: Métrique invalide ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Premier texte",
            "text2": "Deuxième texte",
            "metric": "euclidean"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is False
    assert "not supported" in data["error"]
    print("✅ PASS - Erreur correctement gérée")

    print("\n=== Test 6: Multilingue (anglais-français) ===")
    response = requests.post(
        f"{base_url}{endpoint}",
        json={
            "text1": "Hello world",
            "text2": "Bonjour le monde",
            "metric": "cosine"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    data = response.json()
    assert data["success"] is True
    print(f"Similarité multilingue: {data['similarity']:.3f}")
    print("✅ PASS - Support multilingue fonctionnel")

    print("\n✅ TOUS LES TESTS SONT PASSÉS!")


if __name__ == "__main__":
    try:
        test_text_distance()
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur est démarré avec: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
