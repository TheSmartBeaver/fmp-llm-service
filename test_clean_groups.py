"""
Test pour vérifier que _clean_and_separate_groups_by_depth nettoie correctement les groupes.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator

# Données de test : path_groups avec les anomalies identifiées
test_path_groups_with_anomalies = [
    {
        "group_name": "Métadonnées de cours",
        "keys": [
            "course",
            "topicPath"
        ],
        "format": "Identifiants et chemins de navigation du cours"
    },
    {
        "group_name": "Collection d'exemples",
        "keys": [
            "examplesCollection->examples[x]notes",
            "examplesCollection->examples[x]sentence",
            "examplesCollection->examples[x]translation",
            "examplesCollection->purpose"  # ANOMALIE 1: Ne devrait pas être ici
        ],
        "format": "Phrases d'exemple avec annotations et traductions"
    },
    {
        "group_name": "Exemples dans thèmes (niveau 2)",
        "keys": [
            # ANOMALIE 2: Mélange de profondeurs
            "themes[x]examples[y]explanation",
            "themes[x]examples[y]infinitive",
            "themes[x]examples[y]label",
            "themes[x]examples[y]usageNotes",
            "themes[x]examples[y]conjugation[z]"  # Référence au niveau 3
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
        "group_name": "Groupe Examplescollection",
        "keys": [
            "examplesCollection->examples[x]"
        ],
        "format": "Groupe parent pour examplesCollection"
    },
    {
        "group_name": "Thèmes niveau 1",
        "keys": [
            "themes[x]details",
            "themes[x]explanation",
            "themes[x]name",
            "themes[x]examples[y]",
            "themes[x]groups[y]"
        ],
        "format": "Propriétés descriptives des thèmes"
    }
]


def test_clean_and_separate_groups():
    """Test que le nettoyage des groupes fonctionne correctement."""

    # Créer une instance
    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Appliquer le nettoyage
    result = generator._clean_and_separate_groups_by_depth(test_path_groups_with_anomalies.copy())

    print("=" * 80)
    print("RÉSULTATS DU TEST DE NETTOYAGE")
    print("=" * 80)
    print(f"\nNombre de groupes avant: {len(test_path_groups_with_anomalies)}")
    print(f"Nombre de groupes après: {len(result)}")
    print("\n" + "=" * 80)

    # Vérifications
    print("\nVÉRIFICATIONS DES CORRECTIONS:")
    print("=" * 80)

    # Anomalie 1: examplesCollection->purpose devrait être dans "Groupe Examplescollection"
    print("\n1. Vérification: examplesCollection->purpose")
    found_in_collection = False
    found_in_parent = False

    for group in result:
        if "examplesCollection->purpose" in group["keys"]:
            if "examplesCollection->examples[x]" in group["keys"]:
                found_in_collection = True
                print(f"   ❌ ERREUR: Trouvé dans groupe avec exemples[x]: {group['group_name']}")
            else:
                found_in_parent = True
                print(f"   ✅ OK: Déplacé vers groupe parent: {group['group_name']}")
                print(f"      Clés du groupe: {group['keys']}")

    if not found_in_collection and not found_in_parent:
        print(f"   ❌ ERREUR: Clé non trouvée!")

    # Anomalie 2: Les groupes ne doivent pas mélanger les profondeurs
    print("\n2. Vérification: Séparation des profondeurs")

    import re
    mixed_depth_groups = []

    for group in result:
        depths = set()
        for key in group["keys"]:
            num_vars = len(re.findall(r'\[([x-z])\]', key))
            depths.add(num_vars)

        if len(depths) > 1:
            mixed_depth_groups.append(group)
            print(f"   ❌ ERREUR: Groupe '{group['group_name']}' mélange les profondeurs {depths}")
            print(f"      Clés: {group['keys']}")

    if not mixed_depth_groups:
        print(f"   ✅ OK: Tous les groupes ont une profondeur uniforme")

    # Vérification spécifique: themes[x]examples[y]conjugation[z] devrait être séparé
    print("\n3. Vérification: themes[x]examples[y]conjugation[z] séparé des autres")

    ref_found_with_data = False
    ref_in_separate_group = False

    for group in result:
        if "themes[x]examples[y]conjugation[z]" in group["keys"]:
            # Vérifier si ce groupe contient aussi des clés de niveau 2
            has_level_2 = any(
                "themes[x]examples[y]" in key and "conjugation" not in key
                for key in group["keys"]
            )

            if has_level_2:
                ref_found_with_data = True
                print(f"   ❌ ERREUR: Référence mélangée avec données de niveau 2")
                print(f"      Groupe: {group['group_name']}")
                print(f"      Clés: {group['keys']}")
            else:
                ref_in_separate_group = True
                print(f"   ✅ OK: Référence dans groupe séparé: {group['group_name']}")
                print(f"      Clés: {group['keys']}")

    # Afficher tous les groupes résultants
    print("\n" + "=" * 80)
    print("GROUPES RÉSULTANTS:")
    print("=" * 80)

    for i, group in enumerate(result, 1):
        print(f"\n{i}. {group['group_name']}")
        print(f"   Format: {group['format']}")

        # Calculer la profondeur de ce groupe
        if group["keys"]:
            num_vars = len(re.findall(r'\[([x-z])\]', group["keys"][0]))
            print(f"   Profondeur: {num_vars} variable(s)")

        print(f"   Clés ({len(group['keys'])}):")
        for key in group["keys"]:
            print(f"     - {key}")

    # Sauvegarder dans un fichier JSON pour inspection
    output = {
        "original_count": len(test_path_groups_with_anomalies),
        "result_count": len(result),
        "groups": result
    }

    with open("test_clean_groups_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_clean_groups_output.json")
    print("=" * 80)

    # Résumé final
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES CORRECTIONS:")
    print("=" * 80)

    if found_in_parent and not mixed_depth_groups and ref_in_separate_group:
        print("✅ TOUS LES TESTS PASSENT!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        if not found_in_parent:
            print("   - examplesCollection->purpose n'est pas dans le bon groupe")
        if mixed_depth_groups:
            print(f"   - {len(mixed_depth_groups)} groupe(s) mélangent encore les profondeurs")
        if not ref_in_separate_group:
            print("   - La référence conjugation[z] n'est pas séparée")

    print("=" * 80)


if __name__ == "__main__":
    test_clean_and_separate_groups()
