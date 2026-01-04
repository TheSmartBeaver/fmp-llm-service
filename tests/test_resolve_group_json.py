"""
Test de l'étape 7 : Résolution et expansion des group_json
"""
from app.chains.template_structure_generator import TemplateStructureGenerator
from unittest.mock import MagicMock
import json


def create_generator():
    """Crée une instance de TemplateStructureGenerator pour les tests."""
    mock_db = MagicMock()
    mock_embedding_model = MagicMock()
    return TemplateStructureGenerator(mock_db, mock_embedding_model)


def test_simple_replace_no_variable():
    """Test Exemple 1: Groupe sans variable (simple remplacement)"""
    print("=== Test 1: Simple remplacement (sans variable) ===")

    group_json = {
        "template_name": "text/description_longue",
        "text": "{{irregularVerbs->strategyForIrregulars}}"
    }

    path_to_value_map = {
        "irregularVerbs->strategyForIrregulars": "Pour les irrégularités fréquentes, il est utile de mémoriser..."
    }

    generator = create_generator()
    result = generator._resolve_group_json(group_json, path_to_value_map)

    print("Input group_json:")
    print(json.dumps(group_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    expected = {
        "template_name": "text/description_longue",
        "text": "Pour les irrégularités fréquentes, il est utile de mémoriser..."
    }

    assert result == expected, f"Erreur: {result} != {expected}"
    print("✅ Test réussi!\n")


def test_expansion_with_x():
    """Test Exemple 2: Groupe avec variable [x] (expansion simple)"""
    print("=== Test 2: Expansion avec variable [x] ===")

    group_json = {
        "template_name": "tableaux/tableau_comparatif",
        "title": "Terminaisons",
        "col1_content": "{{conjugationPatterns->endingsByPerson[x]->person}}",
        "col2_content": "{{conjugationPatterns->endingsByPerson[x]->ar}}",
        "col3_content": "{{conjugationPatterns->endingsByPerson[x]->er}}"
    }

    path_to_value_map = {
        "conjugationPatterns->endingsByPerson[0]->person": "yo",
        "conjugationPatterns->endingsByPerson[0]->ar": "-o",
        "conjugationPatterns->endingsByPerson[0]->er": "-o",
        "conjugationPatterns->endingsByPerson[1]->person": "tú",
        "conjugationPatterns->endingsByPerson[1]->ar": "-as",
        "conjugationPatterns->endingsByPerson[1]->er": "-es",
        "conjugationPatterns->endingsByPerson[2]->person": "él/ella",
        "conjugationPatterns->endingsByPerson[2]->ar": "-a",
        "conjugationPatterns->endingsByPerson[2]->er": "-e"
    }

    generator = create_generator()
    result = generator._resolve_group_json(group_json, path_to_value_map)

    print("Input group_json:")
    print(json.dumps(group_json, indent=2, ensure_ascii=False))
    print("\nOutput (3 itérations attendues):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Vérifications
    assert isinstance(result, list), "Le résultat devrait être une liste"
    assert len(result) == 3, f"Devrait avoir 3 itérations, a {len(result)}"

    # Vérifier première itération
    assert result[0]["col1_content"] == "yo"
    assert result[0]["col2_content"] == "-o"
    assert result[0]["col3_content"] == "-o"

    # Vérifier deuxième itération
    assert result[1]["col1_content"] == "tú"
    assert result[1]["col2_content"] == "-as"

    # Vérifier troisième itération
    assert result[2]["col1_content"] == "él/ella"
    assert result[2]["col2_content"] == "-a"

    print("✅ Test réussi!\n")


def test_constant_fields_with_variable():
    """Test Exemple 3: Champ constant + champ avec variable"""
    print("=== Test 3: Champs constants + variables ===")

    group_json = {
        "template_name": "layouts/grid/container",
        "title": "Modèles de verbes",  # Champ constant
        "items": [
            {
                "template_name": "text/concept",
                "label": "{{verbGroups->models[x]->group}}",
                "value": "{{verbGroups->models[x]->infinitive}}"
            }
        ]
    }

    path_to_value_map = {
        "verbGroups->models[0]->group": "-ar",
        "verbGroups->models[0]->infinitive": "hablar",
        "verbGroups->models[1]->group": "-er",
        "verbGroups->models[1]->infinitive": "comer"
    }

    generator = create_generator()
    result = generator._resolve_group_json(group_json, path_to_value_map)

    print("Input group_json:")
    print(json.dumps(group_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Vérifications
    assert isinstance(result, list), "Le résultat devrait être une liste"
    assert len(result) == 2, f"Devrait avoir 2 itérations, a {len(result)}"

    # Vérifier que le champ constant est dupliqué
    assert result[0]["title"] == "Modèles de verbes"
    assert result[1]["title"] == "Modèles de verbes"

    # Vérifier les valeurs variables
    assert result[0]["items"][0]["label"] == "-ar"
    assert result[0]["items"][0]["value"] == "hablar"
    assert result[1]["items"][0]["label"] == "-er"
    assert result[1]["items"][0]["value"] == "comer"

    print("✅ Test réussi! Les champs constants sont dupliqués dans chaque itération.\n")


def test_inline_references():
    """Test Exemple 5: Références inline dans du texte"""
    print("=== Test 4: Références inline ===")

    group_json = {
        "template_name": "text/explication",
        "text": "Le verbe {{verbGroups->models[x]->infinitive}} signifie {{verbGroups->models[x]->translation}} en français."
    }

    path_to_value_map = {
        "verbGroups->models[0]->infinitive": "hablar",
        "verbGroups->models[0]->translation": "parler",
        "verbGroups->models[1]->infinitive": "comer",
        "verbGroups->models[1]->translation": "manger"
    }

    generator = create_generator()
    result = generator._resolve_group_json(group_json, path_to_value_map)

    print("Input group_json:")
    print(json.dumps(group_json, indent=2, ensure_ascii=False))
    print("\nOutput:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Vérifications
    assert isinstance(result, list)
    assert len(result) == 2

    assert result[0]["text"] == "Le verbe hablar signifie parler en français."
    assert result[1]["text"] == "Le verbe comer signifie manger en français."

    print("✅ Test réussi!\n")


def test_nested_arrays():
    """Test avec tableaux imbriqués [x][y]"""
    print("=== Test 5: Tableaux imbriqués (référence de groupe) ===")

    # Groupe 2 : conjugations[y] (sera résolu séparément pour chaque x)
    group_json = {
        "template_name": "tableaux/tableau",
        "rows": [
            {
                "person": "{{irregularVerbs->examples[x]->conjugations[y]->person}}",
                "form": "{{irregularVerbs->examples[x]->conjugations[y]->form}}"
            }
        ]
    }

    # Path map pour x=0 (ser)
    path_to_value_map = {
        "irregularVerbs->examples[0]->conjugations[0]->person": "yo",
        "irregularVerbs->examples[0]->conjugations[0]->form": "soy",
        "irregularVerbs->examples[0]->conjugations[1]->person": "tú",
        "irregularVerbs->examples[0]->conjugations[1]->form": "eres"
    }

    generator = create_generator()

    # D'abord, remplacer [x] par [0] manuellement (simuler ce qui se passerait)
    group_json_with_x0 = {
        "template_name": "tableaux/tableau",
        "rows": [
            {
                "person": "{{irregularVerbs->examples[0]->conjugations[y]->person}}",
                "form": "{{irregularVerbs->examples[0]->conjugations[y]->form}}"
            }
        ]
    }

    result = generator._resolve_group_json(group_json_with_x0, path_to_value_map)

    print("Input group_json (avec x=0):")
    print(json.dumps(group_json_with_x0, indent=2, ensure_ascii=False))
    print("\nOutput:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Vérifications
    assert isinstance(result, list)
    assert len(result) == 2  # 2 conjugaisons

    assert result[0]["rows"][0]["person"] == "yo"
    assert result[0]["rows"][0]["form"] == "soy"
    assert result[1]["rows"][0]["person"] == "tú"
    assert result[1]["rows"][0]["form"] == "eres"

    print("✅ Test réussi!\n")


def test_missing_reference():
    """Test cas limite: référence non trouvée"""
    print("=== Test 6: Référence non trouvée (warning) ===")

    group_json = {
        "template_name": "text/titre",
        "text": "{{metadata->nonExistent}}"
    }

    path_to_value_map = {
        "metadata->course": "Espagnol"
    }

    generator = create_generator()
    result = generator._resolve_group_json(group_json, path_to_value_map)

    print("Input group_json:")
    print(json.dumps(group_json, indent=2, ensure_ascii=False))
    print("\nOutput (devrait garder la référence):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # La référence devrait être gardée telle quelle
    assert result["text"] == "{{metadata->nonExistent}}"

    print("✅ Test réussi! La référence non trouvée est conservée.\n")


if __name__ == "__main__":
    test_simple_replace_no_variable()
    test_expansion_with_x()
    test_constant_fields_with_variable()
    test_inline_references()
    test_nested_arrays()
    test_missing_reference()

    print("=" * 60)
    print("Tous les tests sont passés! ✅")
    print("L'étape 7 est fonctionnelle.")
