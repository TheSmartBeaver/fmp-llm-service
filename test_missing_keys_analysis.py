"""
Test pour analyser pourquoi 39 clés sont manquantes dans resolved_jsons_map.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator

# path_to_value_map fourni par l'utilisateur (simplifié pour le test)
test_path_to_value_map = {
    "course": "Mini cours d'espagnol – Apprendre la conjugaison",
    "topicPath": "string",
    "summary->title": "Principes généraux de la conjugaison espagnole au présent de l'indicatif",
    "summary->explanation": "En espagnol, la conjugaison des verbes dépend du groupe verbal...",
    "themes[0]->name": "Groupes verbaux réguliers",
    "themes[0]->explanation": "Les verbes réguliers se classent en trois groupes...",
    "themes[0]->groups[0]->label": "Verbes en -ar (modèle : hablar)",
    "themes[0]->groups[0]->ending": "-ar",
    "themes[0]->groups[0]->explanation": "Les verbes en -ar forment le groupe le plus vaste...",
    "themes[0]->groups[0]->conjugationTable[0]->person": "1re personne du singulier",
    "themes[0]->groups[0]->conjugationTable[0]->pronoun": "yo",
    "themes[0]->groups[0]->conjugationTable[0]->form": "yo hablo",
    "themes[0]->groups[0]->exampleSentences[0]": "Yo hablo español con mis amigos.",
    "themes[0]->groups[1]->label": "Verbes en -er (modèle : comer)",
    "themes[1]->name": "Verbes irréguliers essentiels",
    "themes[1]->explanation": "Certains verbes très fréquents ne suivent pas les modèles réguliers...",
    "themes[1]->examples[0]->label": "Ser (être)",
    "themes[1]->examples[0]->infinitive": "ser",
    "themes[1]->examples[0]->conjugation[0]->pronoun": "yo",
    "themes[1]->examples[0]->conjugation[0]->form": "soy",
    "themes[2]->name": "Pronoms et omission du sujet",
    "themes[2]->details[0]": "La terminaison verbale permet d'identifier la personne...",
    "relations->similarities": "Les terminaisons des verbes en -er et -ir sont proches...",
    "relations->differences": "Les verbes en -ar ont des terminaisons distinctes...",
    "learningStrategies->principles": "Une progression efficace combine mémorisation ciblée...",
    "learningStrategies->concreteTips[0]": "Choisir un verbe modèle pour chaque groupe...",
    "learningStrategies->pitfallsToAvoid": "Éviter de simplement répéter des tableaux sans contexte.",
    "media->images[0]->label": "Tableau de conjugaison (exemple visuel)",
    "media->images[0]->url": "string",
    "media->videos[0]->label": "Introduction orale au présent de l'indicatif",
    "media->videos[0]->url": "string",
    "examplesCollection->purpose": "Fournir des phrases modèles utilisables immédiatement...",
    "examplesCollection->examples[0]->sentence": "Yo hablo con mi profesora.",
    "examplesCollection->examples[0]->translation": "Je parle avec ma professeure.",
    "glossary[0]->term": "Infinitif",
    "glossary[0]->definition": "Forme nominale du verbe en espagnol...",
}

# Simuler un group_jsons_map incomplet (ce que le LLM pourrait générer)
# IMPORTANT: Ce test simule le cas où le LLM n'a créé que CERTAINS groupes
test_group_jsons_map = {
    "course": "{{course}}",
    "summary->title": "{{summary->title}}",
    # MANQUE: summary->explanation
    "themes[x]": {
        "items": [
            {
                # MANQUE: themes[x]->name
                # MANQUE: themes[x]->explanation
                "themes[x]->groups[y]": {
                    "items": [
                        {
                            # MANQUE: toutes les clés de groups[y]
                        }
                    ]
                }
            }
        ]
    }
    # MANQUE: tous les autres groupes (relations, learningStrategies, media, etc.)
}


def test_missing_keys_analysis():
    """Analyser pourquoi des clés sont manquantes."""
    print("=" * 80)
    print("ANALYSE DES CLÉS MANQUANTES")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Normaliser les clés de path_to_value_map
    normalized_required_keys = {
        generator._normalize_path_to_generic(path)
        for path in test_path_to_value_map.keys()
    }

    print(f"\n📊 Nombre de clés dans path_to_value_map (originales): {len(test_path_to_value_map)}")
    print(f"📊 Nombre de clés normalisées requises: {len(normalized_required_keys)}")

    # Afficher les clés normalisées requises
    print("\n" + "=" * 80)
    print("CLÉS NORMALISÉES REQUISES (de path_to_value_map)")
    print("=" * 80)
    for key in sorted(normalized_required_keys):
        print(f"  - {key}")

    # Extraire les clés de group_jsons_map
    def extract_all_keys(obj, keys_set=None):
        """Extrait toutes les clés présentes dans un objet (récursivement)."""
        if keys_set is None:
            keys_set = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key != "items":
                    keys_set.add(key)
                extract_all_keys(value, keys_set)
        elif isinstance(obj, list):
            for item in obj:
                extract_all_keys(item, keys_set)

        return keys_set

    resolved_keys = extract_all_keys(test_group_jsons_map)

    print(f"\n📊 Nombre de clés dans group_jsons_map: {len(resolved_keys)}")

    print("\n" + "=" * 80)
    print("CLÉS PRÉSENTES DANS group_jsons_map")
    print("=" * 80)
    for key in sorted(resolved_keys):
        print(f"  - {key}")

    # Trouver les clés manquantes
    missing_keys = normalized_required_keys - resolved_keys

    print("\n" + "=" * 80)
    print("ANALYSE DES CLÉS MANQUANTES")
    print("=" * 80)
    print(f"\n❌ {len(missing_keys)} clés manquantes sur {len(normalized_required_keys)} requises")
    print(f"📊 Taux de couverture: {((len(normalized_required_keys) - len(missing_keys)) / len(normalized_required_keys) * 100):.1f}%")

    # Regrouper les clés manquantes par préfixe pour comprendre le pattern
    print("\n" + "=" * 80)
    print("CLÉS MANQUANTES REGROUPÉES PAR PRÉFIXE")
    print("=" * 80)

    # Créer un dictionnaire: préfixe -> liste de clés
    missing_by_prefix = {}
    for key in sorted(missing_keys):
        # Extraire le préfixe (premier niveau)
        if "->" in key:
            prefix = key.split("->")[0]
        elif "[" in key:
            prefix = key.split("[")[0]
        else:
            prefix = key

        if prefix not in missing_by_prefix:
            missing_by_prefix[prefix] = []
        missing_by_prefix[prefix].append(key)

    for prefix, keys in sorted(missing_by_prefix.items()):
        print(f"\n🔍 Préfixe '{prefix}': {len(keys)} clés manquantes")
        for key in keys[:5]:  # Afficher max 5 clés par préfixe
            print(f"   - {key}")
        if len(keys) > 5:
            print(f"   ... et {len(keys) - 5} autres")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC")
    print("=" * 80)

    print("\n🔍 Problème probable:")
    print("   Le LLM n'a pas généré de JSON pour tous les groupes de path_groups.")
    print("   Chaque groupe dans path_groups devrait avoir une entrée correspondante")
    print("   dans group_jsons_map, mais certains sont manquants.")

    print("\n💡 Solutions possibles:")
    print("   1. Vérifier que path_groups contient bien tous les groupes nécessaires")
    print("   2. Vérifier que le LLM génère un JSON pour chaque groupe de path_groups")
    print("   3. Ajouter une validation après la génération pour détecter les groupes manquants")

    # Sauvegarder les résultats
    output = {
        "required_keys_count": len(normalized_required_keys),
        "resolved_keys_count": len(resolved_keys),
        "missing_keys_count": len(missing_keys),
        "coverage_rate": ((len(normalized_required_keys) - len(missing_keys)) / len(normalized_required_keys) * 100),
        "required_keys": sorted(list(normalized_required_keys)),
        "resolved_keys": sorted(list(resolved_keys)),
        "missing_keys": sorted(list(missing_keys)),
        "missing_by_prefix": {k: v for k, v in sorted(missing_by_prefix.items())}
    }

    with open("test_missing_keys_analysis_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_missing_keys_analysis_output.json")
    print("=" * 80)


if __name__ == "__main__":
    test_missing_keys_analysis()
