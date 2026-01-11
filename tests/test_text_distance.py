import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_text_distance_similar_texts():
    """Test avec deux textes très similaires"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Le chat dort sur le canapé",
            "text2": "Le chat dort sur le sofa",
            "metric": "cosine"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["metric"] == "cosine"
    assert data["similarity"] is not None
    assert data["distance"] is not None
    # Textes similaires devraient avoir une haute similarité (> 0.8)
    assert data["similarity"] > 0.8
    # Et une faible distance (< 0.2)
    assert data["distance"] < 0.2


def test_text_distance_different_texts():
    """Test avec deux textes très différents"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Le chat dort sur le canapé",
            "text2": "La programmation informatique est complexe",
            "metric": "cosine"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["metric"] == "cosine"
    assert data["similarity"] is not None
    assert data["distance"] is not None
    # Textes différents devraient avoir une plus faible similarité
    assert data["similarity"] < 0.8


def test_text_distance_identical_texts():
    """Test avec deux textes identiques"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Bonjour le monde",
            "text2": "Bonjour le monde",
            "metric": "cosine"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Textes identiques devraient avoir une similarité très proche de 1
    assert data["similarity"] > 0.99
    # Et une distance très proche de 0
    assert data["distance"] < 0.01


def test_text_distance_semantic_similarity():
    """Test avec des textes sémantiquement similaires mais avec des mots différents"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Un félin se repose",
            "text2": "Un chat dort",
            "metric": "cosine"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Les embeddings devraient capturer la similarité sémantique
    assert data["similarity"] > 0.5


def test_text_distance_default_metric():
    """Test que la métrique par défaut est 'cosine'"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Premier texte",
            "text2": "Deuxième texte"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["metric"] == "cosine"


def test_text_distance_invalid_metric():
    """Test avec une métrique non supportée"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Premier texte",
            "text2": "Deuxième texte",
            "metric": "euclidean"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] is not None
    assert "not supported" in data["error"]


def test_text_distance_empty_texts():
    """Test avec des textes vides"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "",
            "text2": "",
            "metric": "cosine"
        }
    )

    # L'API devrait gérer ce cas (soit retourner une erreur, soit calculer quand même)
    assert response.status_code == 200
    data = response.json()
    # On vérifie juste que la réponse a la bonne structure
    assert "success" in data


def test_text_distance_multilingual():
    """Test avec des textes multilingues (le modèle est multilingual)"""
    response = client.post(
        "/api/utils/text-distance",
        json={
            "text1": "Hello world",
            "text2": "Bonjour le monde",
            "metric": "cosine"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Le modèle multilingual devrait détecter la similarité sémantique
    assert data["similarity"] > 0.5
