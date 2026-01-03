"""
Test pour vérifier que resolved_jsons_map contient toutes les clés nécessaires
pour matcher celles de path_to_value_map.

Ce test simule le processus de création de path_to_value_map et resolved_jsons_map,
puis vérifie que toutes les clés dans path_to_value_map peuvent être trouvées dans
resolved_jsons_map (en tenant compte des variables génériques [x], [y], [z]).
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator


# Données de test : un JSON pédagogique exemple
test_pedagogical_json = {
    "course": "Français",
    "topicPath": "Conjugaison > Passé Composé",
    "summary": {
        "explanation": "Le passé composé est un temps verbal...",
        "title": "Le Passé Composé"
    },
    "examplesCollection": {
        "purpose": "Illustrer l'usage du passé composé",
        "examples": [
            {
                "sentence": "J'ai mangé une pomme",
                "translation": "I ate an apple",
                "notes": "Verbe manger avec avoir"
            },
            {
                "sentence": "Elle est partie",
                "translation": "She left",
                "notes": "Verbe partir avec être"
            }
        ]
    },
    "glossary": [
        {
            "term": "Auxiliaire",
            "definition": "Verbe être ou avoir utilisé pour former le passé composé"
        },
        {
            "term": "Participe passé",
            "definition": "Forme du verbe qui suit l'auxiliaire"
        }
    ],
    "themes": [
        {
            "name": "Verbes avec AVOIR",
            "details": "La majorité des verbes...",
            "examples": [
                {
                    "label": "manger",
                    "infinitive": "manger",
                    "conjugation": [
                        {"pronoun": "je", "form": "ai mangé", "meaning": "I ate"},
                        {"pronoun": "tu", "form": "as mangé", "meaning": "you ate"}
                    ]
                }
            ],
            "groups": [
                {
                    "label": "Verbes en -ER",
                    "ending": "-er",
                    "conjugationTable": [
                        {"person": "1st", "pronoun": "je", "form": "ai + -é", "meaning": "I verbed"}
                    ]
                }
            ]
        }
    ]
}

# Données de test : resolved_jsons_map simulé (ce qui devrait être généré par le LLM)
test_resolved_jsons_map = {
    "course": "course_value",
    "topicPath": "topicPath_value",
    "summary->explanation": "summary_explanation_value",
    "summary->title": "summary_title_value",
    "examplesCollection->purpose": "examplesCollection_purpose_value",
    "examplesCollection->examples[x]": {
        "items": [
            {
                "examplesCollection->examples[x]->sentence": "sentence_value_0",
                "examplesCollection->examples[x]->translation": "translation_value_0",
                "examplesCollection->examples[x]->notes": "notes_value_0"
            }
        ]
    },
    "glossary[x]": {
        "items": [
            {
                "glossary[x]->term": "term_value_0",
                "glossary[x]->definition": "definition_value_0"
            }
        ]
    },
    "themes[x]": {
        "items": [
            {
                "themes[x]->name": "name_value_0",
                "themes[x]->details": "details_value_0",
                "themes[x]->examples[y]": {
                    "items": [
                        {
                            "themes[x]->examples[y]->label": "label_value_0",
                            "themes[x]->examples[y]->infinitive": "infinitive_value_0",
                            "themes[x]->examples[y]->conjugation[z]": {
                                "items": [
                                    {
                                        "themes[x]->examples[y]->conjugation[z]->pronoun": "pronoun_value_0",
                                        "themes[x]->examples[y]->conjugation[z]->form": "form_value_0",
                                        "themes[x]->examples[y]->conjugation[z]->meaning": "meaning_value_0"
                                    }
                                ]
                            }
                        }
                    ]
                },
                "themes[x]->groups[y]": {
                    "items": [
                        {
                            "themes[x]->groups[y]->label": "label_value_0",
                            "themes[x]->groups[y]->ending": "ending_value_0",
                            "themes[x]->groups[y]->conjugationTable[z]": {
                                "items": [
                                    {
                                        "themes[x]->groups[y]->conjugationTable[z]->person": "person_value_0",
                                        "themes[x]->groups[y]->conjugationTable[z]->pronoun": "pronoun_value_0",
                                        "themes[x]->groups[y]->conjugationTable[z]->form": "form_value_0",
                                        "themes[x]->groups[y]->conjugationTable[z]->meaning": "meaning_value_0"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
}


def test_resolved_jsons_coverage():
    """
    Test que resolved_jsons_map contient toutes les clés nécessaires
    pour matcher celles de path_to_value_map.
    """
    # Créer une instance du générateur
    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Étape 1: Créer path_to_value_map à partir du JSON pédagogique
    path_to_value_map = generator._build_path_to_value_map(test_pedagogical_json)

    print("=" * 80)
    print("TEST DE COUVERTURE: resolved_jsons_map vs path_to_value_map")
    print("=" * 80)

    print(f"\n📊 Nombre de chemins dans path_to_value_map: {len(path_to_value_map)}")
    print(f"📊 Nombre de groupes dans resolved_jsons_map: {len(test_resolved_jsons_map)}")

    # Étape 2: Vérifier que chaque clé dans path_to_value_map peut être trouvée dans resolved_jsons_map
    print("\n" + "=" * 80)
    print("VÉRIFICATION DES CLÉS")
    print("=" * 80)

    missing_keys = []
    covered_keys = []

    # Fonction récursive pour extraire toutes les clés de resolved_jsons_map
    def extract_all_keys(obj, keys_set=None):
        """Extrait toutes les clés présentes dans resolved_jsons_map (récursivement)."""
        if keys_set is None:
            keys_set = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key != "items":  # Ne pas ajouter "items" comme clé, mais descendre dans sa valeur
                    keys_set.add(key)
                # Descendre récursivement même si c'est "items"
                extract_all_keys(value, keys_set)
        elif isinstance(obj, list):
            for item in obj:
                extract_all_keys(item, keys_set)

        return keys_set

    # Extraire toutes les clés de resolved_jsons_map
    resolved_keys = extract_all_keys(test_resolved_jsons_map)

    print(f"\n🔍 Nombre total de clés dans resolved_jsons_map (récursif): {len(resolved_keys)}")

    # Pour chaque clé dans path_to_value_map, vérifier si elle existe dans resolved_keys
    for path in sorted(path_to_value_map.keys()):
        # Normaliser le chemin (remplacer les indices réels par des variables génériques)
        normalized_path = generator._normalize_path_to_generic(path)

        if normalized_path in resolved_keys:
            covered_keys.append(path)
            print(f"✅ {path} → {normalized_path}")
        else:
            missing_keys.append(path)
            print(f"❌ {path} → {normalized_path} (MANQUANT dans resolved_jsons_map)")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    coverage_rate = (len(covered_keys) / len(path_to_value_map)) * 100 if path_to_value_map else 0

    print(f"\n📊 Clés couvertes: {len(covered_keys)} / {len(path_to_value_map)} ({coverage_rate:.1f}%)")
    print(f"📊 Clés manquantes: {len(missing_keys)}")

    if missing_keys:
        print("\n❌ CLÉS MANQUANTES DANS resolved_jsons_map:")
        for key in missing_keys:
            normalized = generator._normalize_path_to_generic(key)
            print(f"   - {key} (normalisé: {normalized})")
    else:
        print("\n✅ TOUTES LES CLÉS SONT COUVERTES!")

    # Afficher les clés dans resolved_jsons_map
    print("\n" + "=" * 80)
    print("CLÉS PRÉSENTES DANS resolved_jsons_map")
    print("=" * 80)
    for key in sorted(resolved_keys):
        print(f"  - {key}")

    # Afficher la structure complète de resolved_jsons_map pour debugging
    print("\n" + "=" * 80)
    print("STRUCTURE COMPLÈTE DE resolved_jsons_map (pour debugging)")
    print("=" * 80)
    print(json.dumps(test_resolved_jsons_map, indent=2, ensure_ascii=False))

    # Afficher les clés dans path_to_value_map
    print("\n" + "=" * 80)
    print("CLÉS PRÉSENTES DANS path_to_value_map (normalisées)")
    print("=" * 80)
    normalized_paths = {generator._normalize_path_to_generic(path) for path in path_to_value_map.keys()}
    for key in sorted(normalized_paths):
        print(f"  - {key}")

    # Sauvegarder les résultats
    output = {
        "path_to_value_map_count": len(path_to_value_map),
        "resolved_jsons_map_keys_count": len(resolved_keys),
        "coverage_rate": coverage_rate,
        "covered_keys": covered_keys,
        "missing_keys": missing_keys,
        "resolved_keys": sorted(list(resolved_keys)),
        "path_to_value_map_normalized": sorted(list(normalized_paths))
    }

    with open("test_resolved_jsons_coverage_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_resolved_jsons_coverage_output.json")
    print("=" * 80)

    # Assertion finale
    if missing_keys:
        print("\n❌ TEST ÉCHOUÉ: Certaines clés ne sont pas couvertes")
    else:
        print("\n✅ TEST RÉUSSI: Toutes les clés sont couvertes")

    print("=" * 80)


if __name__ == "__main__":
    test_resolved_jsons_coverage()
