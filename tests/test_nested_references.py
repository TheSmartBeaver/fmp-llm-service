"""
Test pour vérifier que _add_missing_nested_references insère correctement les références manquantes.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator

# Données de test : path_groups similaire à l'exemple fourni
test_path_groups = [
    {
        "group_name": "Métadonnées de cours",
        "keys": [
            "course",
            "topicPath"
        ],
        "format": "Identifiants et chemins de navigation du cours"
    },
    {
        "group_name": "Résumé et relations",
        "keys": [
            "summary->explanation",
            "summary->title",
            "relations->differences",
            "relations->practicalLinks",
            "relations->similarities"
        ],
        "format": "Textes descriptifs et comparatifs du sujet"
    },
    {
        "group_name": "Stratégies d'apprentissage",
        "keys": [
            "learningStrategies->concreteTips",
            "learningStrategies->pitfallsToAvoid",
            "learningStrategies->principles"
        ],
        "format": "Conseils pédagogiques et points clés"
    },
    {
        "group_name": "Collection d'exemples",
        "keys": [
            "examplesCollection->examples[x]notes",
            "examplesCollection->examples[x]sentence",
            "examplesCollection->examples[x]translation",
            "examplesCollection->purpose"
        ],
        "format": "Phrases d'exemple avec annotations et traductions"
    },
    {
        "group_name": "Glossaire simple",
        "keys": [
            "glossary[x]definition",
            "glossary[x]term"
        ],
        "format": "Termes avec définitions"
    },
    {
        "group_name": "Ressources médias images",
        "keys": [
            "media->images[x]label",
            "media->images[x]url",
            "media->images[x]usageSuggestion"
        ],
        "format": "Images avec étiquettes et contexte d'utilisation"
    },
    {
        "group_name": "Ressources médias vidéos",
        "keys": [
            "media->videos[x]label",
            "media->videos[x]start",
            "media->videos[x]url",
            "media->videos[x]usageSuggestion"
        ],
        "format": "Vidéos avec timestamps de démarrage et suggestions d'usage"
    },
    {
        "group_name": "Thèmes niveau 1",
        "keys": [
            "themes[x]details",
            "themes[x]explanation",
            "themes[x]name"
        ],
        "format": "Propriétés descriptives des thèmes"
    },
    {
        "group_name": "Exemples dans thèmes (niveau 2)",
        "keys": [
            "themes[x]examples[y]explanation",
            "themes[x]examples[y]infinitive",
            "themes[x]examples[y]label",
            "themes[x]examples[y]usageNotes"
        ],
        "format": "Données d'exemple simple avec infinitif et notes"
    },
    {
        "group_name": "Conjugaisons dans exemples (niveau 3)",
        "keys": [
            "themes[x]examples[y]conjugation[z]form",
            "themes[x]examples[y]conjugation[z]meaning",
            "themes[x]examples[y]conjugation[z]pronoun"
        ],
        "format": "Formes conjuguées avec pronoms et significations"
    },
    {
        "group_name": "Groupes dans thèmes (niveau 2)",
        "keys": [
            "themes[x]groups[y]ending",
            "themes[x]groups[y]exampleSentences",
            "themes[x]groups[y]explanation",
            "themes[x]groups[y]label"
        ],
        "format": "Groupes de conjugaison avec finales et phrases d'exemple"
    },
    {
        "group_name": "Tables de conjugaison (niveau 3)",
        "keys": [
            "themes[x]groups[y]conjugationTable[z]form",
            "themes[x]groups[y]conjugationTable[z]meaning",
            "themes[x]groups[y]conjugationTable[z]person",
            "themes[x]groups[y]conjugationTable[z]pronoun",
            "themes[x]groups[y]conjugationTable[z]translation"
        ],
        "format": "Entrées structurées de conjugaison avec personne, pronom et traduction"
    }
]


def test_add_missing_nested_references():
    """Test que les références manquantes sont correctement ajoutées."""

    # Créer une instance (nous n'avons pas besoin de DB pour ce test)
    # On va juste tester les méthodes utilitaires
    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Appliquer la transformation
    result = generator._add_missing_nested_references(test_path_groups.copy())

    print("=" * 80)
    print("RÉSULTATS DU TEST")
    print("=" * 80)
    print(f"\nNombre de groupes avant: {len(test_path_groups)}")
    print(f"Nombre de groupes après: {len(result)}")
    print("\n" + "=" * 80)

    # Vérifications attendues :
    expected_refs = {
        "examplesCollection->examples[x]": "Collection d'exemples",
        "glossary[x]": "Nouveau groupe (glossary racine)",
        "media->images[x]": "Nouveau groupe (media parent fusionné)",
        "media->videos[x]": "Nouveau groupe (media parent fusionné)",
        "themes[x]": "Nouveau groupe (themes racine)",
        "themes[x]examples[y]": "Thèmes niveau 1",
        "themes[x]groups[y]": "Thèmes niveau 1",
        "themes[x]examples[y]conjugation[z]": "Exemples dans thèmes (niveau 2)",
        "themes[x]groups[y]conjugationTable[z]": "Groupes dans thèmes (niveau 2)",
    }

    print("\nVÉRIFICATIONS DES RÉFÉRENCES ATTENDUES:")
    print("=" * 80)

    for ref, expected_location in expected_refs.items():
        found = False
        found_in = None

        for group in result:
            if ref in group["keys"]:
                found = True
                found_in = group["group_name"]
                break

        status = "✅" if found else "❌"
        print(f"{status} {ref}")
        if found:
            print(f"   → Trouvé dans: {found_in}")
        else:
            print(f"   → MANQUANT (attendu dans: {expected_location})")
        print()

    # Afficher tous les groupes résultants
    print("\n" + "=" * 80)
    print("GROUPES RÉSULTANTS:")
    print("=" * 80)

    for i, group in enumerate(result, 1):
        print(f"\n{i}. {group['group_name']}")
        print(f"   Format: {group['format']}")
        print(f"   Clés ({len(group['keys'])}):")
        for key in group["keys"]:
            print(f"     - {key}")

    # Sauvegarder dans un fichier JSON pour inspection
    output = {
        "original_count": len(test_path_groups),
        "result_count": len(result),
        "groups": result
    }

    with open("test_nested_references_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_nested_references_output.json")
    print("=" * 80)


if __name__ == "__main__":
    test_add_missing_nested_references()
