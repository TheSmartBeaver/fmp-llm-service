"""
Test de la fonction _build_path_to_value_map (Étape 6)
"""
from app.chains.template_structure_generator import TemplateStructureGenerator
from unittest.mock import MagicMock
import json


def create_generator():
    """Crée une instance de TemplateStructureGenerator pour les tests."""
    mock_db = MagicMock()
    mock_embedding_model = MagicMock()
    return TemplateStructureGenerator(mock_db, mock_embedding_model)


def test_simple_dict():
    """Test avec un dictionnaire simple (pas de tableaux)"""
    print("=== Test 1: Dictionnaire simple ===")

    source_json = {
        "metadata": {
            "course": "Mini cours d'espagnol",
            "language": "fr"
        },
        "overview": {
            "purpose": "Apprendre la conjugaison"
        }
    }

    generator = create_generator()
    result = generator._build_path_to_value_map(source_json)

    print("Input:")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    for path, value in sorted(result.items()):
        print(f"  {path}: {value}")

    expected = {
        "metadata->course": "Mini cours d'espagnol",
        "metadata->language": "fr",
        "overview->purpose": "Apprendre la conjugaison"
    }

    assert result == expected, f"Erreur: {result} != {expected}"
    print("✅ Test réussi!\n")


def test_simple_array():
    """Test avec un tableau simple"""
    print("=== Test 2: Tableau simple ===")

    source_json = {
        "verbGroups": {
            "models": [
                {"group": "-ar", "infinitive": "hablar"},
                {"group": "-er", "infinitive": "comer"},
                {"group": "-ir", "infinitive": "vivir"}
            ]
        }
    }

    generator = create_generator()
    result = generator._build_path_to_value_map(source_json)

    print("Input:")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    for path, value in sorted(result.items()):
        print(f"  {path}: {value}")

    expected = {
        "verbGroups->models[0]->group": "-ar",
        "verbGroups->models[0]->infinitive": "hablar",
        "verbGroups->models[1]->group": "-er",
        "verbGroups->models[1]->infinitive": "comer",
        "verbGroups->models[2]->group": "-ir",
        "verbGroups->models[2]->infinitive": "vivir"
    }

    assert result == expected, f"Erreur: {result} != {expected}"
    print("✅ Test réussi!\n")


def test_nested_arrays():
    """Test avec des tableaux imbriqués"""
    print("=== Test 3: Tableaux imbriqués ===")

    source_json = {
        "irregularVerbs": {
            "examples": [
                {
                    "verb": "ser",
                    "conjugations": [
                        {"person": "yo", "form": "soy"},
                        {"person": "tú", "form": "eres"}
                    ]
                },
                {
                    "verb": "tener",
                    "conjugations": [
                        {"person": "yo", "form": "tengo"},
                        {"person": "tú", "form": "tienes"}
                    ]
                }
            ]
        }
    }

    generator = create_generator()
    result = generator._build_path_to_value_map(source_json)

    print("Input:")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    for path, value in sorted(result.items()):
        print(f"  {path}: {value}")

    expected = {
        "irregularVerbs->examples[0]->verb": "ser",
        "irregularVerbs->examples[0]->conjugations[0]->person": "yo",
        "irregularVerbs->examples[0]->conjugations[0]->form": "soy",
        "irregularVerbs->examples[0]->conjugations[1]->person": "tú",
        "irregularVerbs->examples[0]->conjugations[1]->form": "eres",
        "irregularVerbs->examples[1]->verb": "tener",
        "irregularVerbs->examples[1]->conjugations[0]->person": "yo",
        "irregularVerbs->examples[1]->conjugations[0]->form": "tengo",
        "irregularVerbs->examples[1]->conjugations[1]->person": "tú",
        "irregularVerbs->examples[1]->conjugations[1]->form": "tienes"
    }

    assert result == expected, f"Erreur: {result} != {expected}"
    print("✅ Test réussi!\n")


def test_mixed_types():
    """Test avec différents types de valeurs"""
    print("=== Test 4: Types de valeurs variés ===")

    source_json = {
        "title": "Mon cours",
        "count": 42,
        "active": True,
        "score": 3.14,
        "tags": ["python", "api"],
        "metadata": None
    }

    generator = create_generator()
    result = generator._build_path_to_value_map(source_json)

    print("Input:")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    for path, value in sorted(result.items()):
        print(f"  {path}: {value!r}")

    expected = {
        "title": "Mon cours",
        "count": 42,
        "active": True,
        "score": 3.14,
        "tags[0]": "python",
        "tags[1]": "api",
        "metadata": None
    }

    assert result == expected, f"Erreur: {result} != {expected}"
    print("✅ Test réussi!\n")


def test_complex_spanish_example():
    """Test avec un extrait du JSON espagnol réel"""
    print("=== Test 5: Extrait du JSON espagnol ===")

    source_json = {
        "metadata": {
            "course": "Mini cours d'espagnol — Conjugaison",
            "language": "fr"
        },
        "conjugationPatterns": {
            "generalExplanation": "Au présent de l'indicatif...",
            "endingsByPerson": [
                {"person": "yo", "ar": "-o", "er": "-o", "ir": "-o"},
                {"person": "tú", "ar": "-as", "er": "-es", "ir": "-es"},
                {"person": "él/ella", "ar": "-a", "er": "-e", "ir": "-e"}
            ]
        }
    }

    generator = create_generator()
    result = generator._build_path_to_value_map(source_json)

    print("Input (extrait):")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))
    print(f"\nOutput ({len(result)} chemins trouvés):")
    for path, value in sorted(result.items()):
        print(f"  {path}: {value}")

    # Vérifier quelques chemins clés
    assert result["metadata->course"] == "Mini cours d'espagnol — Conjugaison"
    assert result["metadata->language"] == "fr"
    assert result["conjugationPatterns->generalExplanation"] == "Au présent de l'indicatif..."
    assert result["conjugationPatterns->endingsByPerson[0]->person"] == "yo"
    assert result["conjugationPatterns->endingsByPerson[0]->ar"] == "-o"
    assert result["conjugationPatterns->endingsByPerson[1]->person"] == "tú"
    assert result["conjugationPatterns->endingsByPerson[2]->ar"] == "-a"

    print("✅ Test réussi!\n")


if __name__ == "__main__":
    test_simple_dict()
    test_simple_array()
    test_nested_arrays()
    test_mixed_types()
    test_complex_spanish_example()

    print("=" * 60)
    print("Tous les tests sont passés! ✅")
    print("L'étape 6 est fonctionnelle.")
