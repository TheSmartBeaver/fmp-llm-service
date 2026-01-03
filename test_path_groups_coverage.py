"""
Test pour vérifier que path_groups contient bien tous les groupes nécessaires
pour couvrir toutes les clés de path_to_value_map.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator

# path_to_value_map fourni (échantillon)
test_path_to_value_map = {
    "course": "Mini cours d'espagnol",
    "topicPath": "string",
    "summary->title": "Principes généraux",
    "summary->explanation": "En espagnol...",
    "themes[0]->name": "Groupes verbaux réguliers",
    "themes[0]->explanation": "Les verbes réguliers...",
    "themes[0]->groups[0]->label": "Verbes en -ar",
    "themes[0]->groups[0]->ending": "-ar",
    "themes[0]->groups[0]->conjugationTable[0]->person": "1re personne",
    "themes[0]->groups[0]->conjugationTable[0]->pronoun": "yo",
    "themes[0]->groups[0]->exampleSentences[0]": "Yo hablo español",
    "themes[1]->name": "Verbes irréguliers",
    "themes[1]->examples[0]->label": "Ser (être)",
    "themes[1]->examples[0]->infinitive": "ser",
    "themes[1]->examples[0]->conjugation[0]->pronoun": "yo",
    "themes[1]->examples[0]->conjugation[0]->form": "soy",
    "themes[2]->name": "Pronoms et omission",
    "themes[2]->details[0]": "La terminaison verbale...",
    "relations->similarities": "Les terminaisons...",
    "relations->differences": "Les verbes en -ar...",
    "learningStrategies->principles": "Une progression efficace...",
    "learningStrategies->concreteTips[0]": "Choisir un verbe modèle...",
    "learningStrategies->pitfallsToAvoid": "Éviter de simplement répéter...",
    "media->images[0]->label": "Tableau de conjugaison",
    "media->images[0]->url": "string",
    "media->videos[0]->label": "Introduction orale",
    "media->videos[0]->url": "string",
    "examplesCollection->purpose": "Fournir des phrases modèles...",
    "examplesCollection->examples[0]->sentence": "Yo hablo con mi profesora.",
    "examplesCollection->examples[0]->translation": "Je parle avec ma professeure.",
    "glossary[0]->term": "Infinitif",
    "glossary[0]->definition": "Forme nominale du verbe...",
}


def test_path_groups_coverage():
    """
    Tester si path_groups contient tous les groupes nécessaires
    pour couvrir path_to_value_map.
    """
    print("=" * 80)
    print("ANALYSE DE LA COUVERTURE DE path_groups")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Normaliser les clés de path_to_value_map
    normalized_required_keys = {
        generator._normalize_path_to_generic(path)
        for path in test_path_to_value_map.keys()
    }

    print(f"\n📊 Nombre de clés normalisées requises: {len(normalized_required_keys)}")

    # Afficher les clés requises groupées par préfixe
    print("\n" + "=" * 80)
    print("CLÉS REQUISES GROUPÉES PAR GROUPE/PRÉFIXE")
    print("=" * 80)

    # Regrouper par préfixe pour identifier les groupes attendus
    keys_by_group = {}
    for key in sorted(normalized_required_keys):
        # Extraire le groupe (avant la première variable ou ->)
        if "[x]" in key:
            # Ex: "themes[x]->name" -> groupe "themes[x]"
            group = key.split("->")[0] if "->" in key else key.split("[")[0] + "[x]"
        elif "->" in key:
            # Ex: "summary->title" -> groupe "summary"
            parts = key.split("->")
            # Trouver la partie avec la première variable ou le premier niveau
            if "[" in parts[0]:
                group = parts[0]
            else:
                group = parts[0]
        else:
            # Ex: "course" -> groupe "course"
            group = key

        if group not in keys_by_group:
            keys_by_group[group] = []
        keys_by_group[group].append(key)

    for group, keys in sorted(keys_by_group.items()):
        print(f"\n🔍 Groupe '{group}': {len(keys)} clés")
        for key in keys[:3]:
            print(f"   - {key}")
        if len(keys) > 3:
            print(f"   ... et {len(keys) - 3} autres")

    print("\n" + "=" * 80)
    print("GROUPES path_groups ATTENDUS")
    print("=" * 80)
    print("\nPour couvrir toutes les clés, path_groups devrait contenir au moins:")

    expected_groups = set()
    for key in normalized_required_keys:
        # Extraire tous les niveaux de groupe possibles
        # Ex: "themes[x]->groups[y]->label" devrait avoir:
        #   - Un groupe pour "themes[x]" avec clés "themes[x]->name", "themes[x]->explanation", etc.
        #   - Un groupe pour "themes[x]->groups[y]" avec clés "themes[x]->groups[y]->label", etc.

        parts = key.replace("->", ".").split(".")
        cumulative_path = ""

        for i, part in enumerate(parts):
            if i == 0:
                cumulative_path = part
            else:
                cumulative_path += "->" + part if "->" not in cumulative_path or "[" not in parts[i-1] else part

            # Ajouter comme groupe si c'est une référence avec variable ou un préfixe simple
            if "[x]" in cumulative_path or "[y]" in cumulative_path or "[z]" in cumulative_path:
                expected_groups.add(cumulative_path)
            elif i == 0 and "[" not in part:
                # Premier niveau sans variable (ex: "course", "summary", "relations")
                expected_groups.add(part)

    # Simplifier: regrouper par préfixe principal
    main_groups = set()
    for key in normalized_required_keys:
        if "->" in key:
            prefix = key.split("->")[0]
        elif "[x]" in key:
            prefix = key.split("[")[0] + "[x]"
        else:
            prefix = key
        main_groups.add(prefix)

    print(f"\n📊 Nombre de groupes principaux attendus: {len(main_groups)}")
    for group in sorted(main_groups):
        print(f"   - {group}")

    print("\n" + "=" * 80)
    print("RECOMMANDATIONS")
    print("=" * 80)

    print("\n💡 Pour que resolved_jsons_map couvre 100% des clés:")
    print("   1. path_groups doit contenir un groupe pour chaque préfixe principal")
    print("   2. Chaque groupe dans path_groups doit lister TOUTES ses clés")
    print("   3. Le LLM doit générer un JSON pour CHAQUE groupe de path_groups")
    print("   4. _resolve_group_references doit résoudre toutes les références imbriquées")

    print("\n⚠️  Problème actuel détecté:")
    print("   - path_to_value_map contient des clés de multiples groupes")
    print(f"   - Il faut au minimum {len(main_groups)} groupes dans path_groups")
    print("   - Chaque groupe doit ensuite être transformé en JSON par le LLM")

    # Sauvegarder
    output = {
        "required_keys_count": len(normalized_required_keys),
        "main_groups_count": len(main_groups),
        "required_keys": sorted(list(normalized_required_keys)),
        "main_groups": sorted(list(main_groups)),
        "keys_by_group": {k: v for k, v in sorted(keys_by_group.items())}
    }

    with open("test_path_groups_coverage_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_path_groups_coverage_output.json")
    print("=" * 80)


if __name__ == "__main__":
    test_path_groups_coverage()
