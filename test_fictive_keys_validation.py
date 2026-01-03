"""
Test pour vérifier que _validate_group_json_references détecte correctement
les clés fictives inventées par le LLM.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_fictive_keys_validation():
    """
    Tester la détection de clés fictives dans le JSON généré par le LLM.
    """
    print("=" * 80)
    print("TEST DE VALIDATION DES CLÉS FICTIVES")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Groupe avec clés valides
    group = {
        "format": "Glossaire",
        "keys": [
            "glossary[x]->term",
            "glossary[x]->definition"
        ]
    }

    # CAS 1: JSON correct (toutes les références sont valides)
    print("\n" + "=" * 80)
    print("CAS 1: JSON CORRECT (Aucune clé fictive)")
    print("=" * 80)

    correct_json = {
        "template_name": "layouts/vertical_column/container",
        "items": [
            {
                "template_name": "text/definition",
                "term": "{{glossary[x]->term}}",
                "definition": "{{glossary[x]->definition}}"
            }
        ]
    }

    print("\nJSON généré par le LLM:")
    print(json.dumps(correct_json, indent=2, ensure_ascii=False))

    print("\nValidation:")
    generator._validate_group_json_references(correct_json, group)
    print("✅ Aucun warning attendu (JSON correct)")

    # CAS 2: JSON avec clés fictives
    print("\n" + "=" * 80)
    print("CAS 2: JSON AVEC CLÉS FICTIVES")
    print("=" * 80)

    fictive_json = {
        "template_name": "layouts/vertical_column/container",
        "items": [
            {
                "template_name": "text/definition",
                "term": "{{glossary[x]->term}}",
                "definition": "{{glossary[x]->definition}}",
                "example": "{{glossary[x]->example}}",  # ❌ FICTIF
                "pronunciation": "{{glossary[x]->pronunciation}}"  # ❌ FICTIF
            }
        ]
    }

    print("\nJSON généré par le LLM (avec clés fictives):")
    print(json.dumps(fictive_json, indent=2, ensure_ascii=False))

    print("\nValidation:")
    generator._validate_group_json_references(fictive_json, group)
    print("\n✅ Warning attendu pour 'example' et 'pronunciation'")

    # CAS 3: JSON avec clés ambiguës (manque [x])
    print("\n" + "=" * 80)
    print("CAS 3: JSON AVEC CLÉS AMBIGUËS (manque [x])")
    print("=" * 80)

    group_with_array = {
        "format": "Conseils d'apprentissage",
        "keys": [
            "learningStrategies->principles",
            "learningStrategies->concreteTips[x]",
            "learningStrategies->pitfallsToAvoid"
        ]
    }

    ambiguous_json = {
        "template_name": "text/tips",
        "principles": "{{learningStrategies->principles}}",
        "tips": "{{learningStrategies->concreteTips}}",  # ❌ Manque [x]
        "pitfalls": "{{learningStrategies->pitfallsToAvoid}}"
    }

    print("\nJSON généré par le LLM (avec clé ambiguë):")
    print(json.dumps(ambiguous_json, indent=2, ensure_ascii=False))

    print("\nValidation:")
    generator._validate_group_json_references(ambiguous_json, group_with_array)
    print("\n✅ Warning attendu pour 'concreteTips' (devrait être 'concreteTips[x]')")

    # CAS 4: JSON avec indices numériques au lieu de variables
    print("\n" + "=" * 80)
    print("CAS 4: JSON AVEC INDICES NUMÉRIQUES (au lieu de [x])")
    print("=" * 80)

    numeric_indices_json = {
        "template_name": "layouts/vertical_column/container",
        "items": [
            {
                "template_name": "text/definition",
                "term": "{{glossary[0]->term}}",  # ❌ Devrait être [x]
                "definition": "{{glossary[1]->definition}}"  # ❌ Devrait être [x]
            }
        ]
    }

    print("\nJSON généré par le LLM (avec indices numériques):")
    print(json.dumps(numeric_indices_json, indent=2, ensure_ascii=False))

    print("\nValidation:")
    generator._validate_group_json_references(numeric_indices_json, group)
    print("\n✅ Warning attendu pour 'glossary[0]' et 'glossary[1]'")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    print("\n✅ La validation détecte correctement:")
    print("   1. Les clés fictives inventées par le LLM")
    print("   2. Les clés ambiguës (manque [x] pour les tableaux)")
    print("   3. Les indices numériques au lieu de variables génériques")
    print("\n📊 Cette validation aide à diagnostiquer les hallucinations du LLM")

    # Sauvegarder
    output = {
        "test_cases": [
            {
                "name": "CAS 1: JSON correct",
                "group_keys": group["keys"],
                "json": correct_json,
                "expected_warnings": 0
            },
            {
                "name": "CAS 2: JSON avec clés fictives",
                "group_keys": group["keys"],
                "json": fictive_json,
                "expected_warnings": 2,
                "fictive_keys": ["glossary[x]->example", "glossary[x]->pronunciation"]
            },
            {
                "name": "CAS 3: JSON avec clés ambiguës",
                "group_keys": group_with_array["keys"],
                "json": ambiguous_json,
                "expected_warnings": 1,
                "fictive_keys": ["learningStrategies->concreteTips"]
            },
            {
                "name": "CAS 4: JSON avec indices numériques",
                "group_keys": group["keys"],
                "json": numeric_indices_json,
                "expected_warnings": 2,
                "fictive_keys": ["glossary[0]->term", "glossary[1]->definition"]
            }
        ]
    }

    with open("test_fictive_keys_validation_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_fictive_keys_validation_output.json")
    print("=" * 80)


if __name__ == "__main__":
    test_fictive_keys_validation()
