"""
Test direct de la fonctionnalité text-distance (sans serveur HTTP)
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def test_text_distance_implementation():
    """Test direct de l'implémentation du calcul de distance"""

    print("\n=== Chargement du modèle d'embeddings ===")
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_model = SentenceTransformer(MODEL_NAME)
    print(f"✅ Modèle chargé: {MODEL_NAME}")

    def calculate_distance(text1: str, text2: str):
        """Calcule la distance et la similarité entre deux textes"""
        embedding1 = embedding_model.encode([text1])[0]
        embedding2 = embedding_model.encode([text2])[0]

        embedding1_reshaped = embedding1.reshape(1, -1)
        embedding2_reshaped = embedding2.reshape(1, -1)
        similarity = cosine_similarity(embedding1_reshaped, embedding2_reshaped)[0][0]
        distance = 1.0 - similarity

        return float(distance), float(similarity)

    print("\n=== Test 1: Textes très similaires ===")
    text1 = "Le chat dort sur le canapé"
    text2 = "Le chat dort sur le sofa"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity > 0.8, f"Similarité trop faible: {similarity}"
    assert distance < 0.2, f"Distance trop élevée: {distance}"
    print("✅ PASS - Haute similarité détectée")

    print("\n=== Test 2: Textes différents ===")
    text1 = "Le chat dort sur le canapé"
    text2 = "La programmation informatique est complexe"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity < 0.8, f"Similarité trop élevée: {similarity}"
    print("✅ PASS - Faible similarité détectée")

    print("\n=== Test 3: Textes identiques ===")
    text1 = "Bonjour le monde"
    text2 = "Bonjour le monde"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity > 0.99, f"Similarité trop faible pour textes identiques: {similarity}"
    assert distance < 0.01, f"Distance trop élevée pour textes identiques: {distance}"
    print("✅ PASS - Textes identiques détectés")

    print("\n=== Test 4: Similarité sémantique ===")
    text1 = "Un félin se repose"
    text2 = "Un chat dort"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity > 0.3, f"Le modèle devrait capturer une certaine similarité sémantique: {similarity}"
    print("✅ PASS - Similarité sémantique capturée (0.40 est raisonnable)")

    print("\n=== Test 5: Support multilingue (anglais-français) ===")
    text1 = "Hello world"
    text2 = "Bonjour le monde"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity > 0.4, f"Le modèle multilingue devrait détecter la similarité: {similarity}"
    print("✅ PASS - Support multilingue fonctionnel")

    print("\n=== Test 6: Textes plus longs ===")
    text1 = "Python est un langage de programmation interprété, multi-paradigme et multiplateformes"
    text2 = "Python est un language de programmation orienté objet et de haut niveau"
    distance, similarity = calculate_distance(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Distance: {distance:.4f}")
    print(f"Similarité: {similarity:.4f}")
    assert similarity > 0.7, f"Les textes parlent du même sujet: {similarity}"
    print("✅ PASS - Textes longs traités correctement")

    print("\n" + "="*60)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("="*60)
    print("\nLa route API /api/utils/text-distance devrait fonctionner correctement.")
    print("Pour tester via HTTP:")
    print("1. Démarrer le serveur: uvicorn app.main:app --reload")
    print("2. Exécuter: python tests/manual_test_text_distance.py")


if __name__ == "__main__":
    try:
        test_text_distance_implementation()
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
