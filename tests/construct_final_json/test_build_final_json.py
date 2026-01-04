"""
Script de test pour la construction incrémentale du final_json.

Ce script utilise les données de entry.py et applique l'algorithme
de construction incrémentale pour générer le final_json.
"""

import json
import sys
from pathlib import Path

# Ajouter le chemin parent pour pouvoir importer entry
sys.path.insert(0, str(Path(__file__).parent))

from entry import entry, group_jsons_map, final_json as expected_final_json
from build_final_json import build_final_json_incremental, print_json_preview


def test_incremental_build():
    """
    Test de la construction incrémentale du final_json.
    """
    print("\n" + "=" * 80)
    print("TEST DE CONSTRUCTION INCRÉMENTALE DU FINAL_JSON")
    print("=" * 80)
    print(f"\nDonnées d'entrée:")
    print(f"  - entry: {len(entry)} chemins")
    print(f"  - group_jsons_map: {len(group_jsons_map)} templates")
    print(f"  - expected_final_json: {len(expected_final_json)} templates")

    # Construire le final_json de manière incrémentale
    result = build_final_json_incremental(
        entry=entry,
        group_jsons_map=group_jsons_map,
        verbose=True  # Afficher tous les détails
    )

    print("\n" + "=" * 80)
    print("RÉSULTAT FINAL")
    print("=" * 80)
    print(f"\nNombre de templates générés: {len(result)}")
    print(f"Nombre de templates attendus: {len(expected_final_json)}")

    # Sauvegarder le résultat dans un fichier JSON
    output_file = Path(__file__).parent / "generated_final_json.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Résultat sauvegardé dans: {output_file}")

    # Afficher un aperçu des premiers templates
    print("\n" + "-" * 80)
    print("APERÇU DES PREMIERS TEMPLATES GÉNÉRÉS:")
    print("-" * 80)

    for i, template in enumerate(result[:3]):  # Afficher les 3 premiers
        print(f"\nTemplate #{i}:")
        print_json_preview(template, max_depth=3)
        print()

    if len(result) > 3:
        print(f"... et {len(result) - 3} autres templates")

    return result


def compare_with_expected():
    """
    Compare le résultat généré avec le résultat attendu.
    """
    print("\n" + "=" * 80)
    print("COMPARAISON AVEC LE RÉSULTAT ATTENDU")
    print("=" * 80)

    result = build_final_json_incremental(
        entry=entry,
        group_jsons_map=group_jsons_map,
        verbose=False  # Pas de logs pour cette comparaison
    )

    print(f"\nRésultat généré: {len(result)} templates")
    print(f"Résultat attendu: {len(expected_final_json)} templates")

    if len(result) != len(expected_final_json):
        print(f"\n⚠️  DIFFÉRENCE: Nombre de templates différent!")
        print(f"   Généré: {len(result)}")
        print(f"   Attendu: {len(expected_final_json)}")
    else:
        print(f"\n✓ Même nombre de templates")

    # Comparer le contenu (en JSON string pour faciliter la comparaison)
    result_json = json.dumps(result, sort_keys=True, ensure_ascii=False)
    expected_json = json.dumps(expected_final_json, sort_keys=True, ensure_ascii=False)

    if result_json == expected_json:
        print("✓ Le contenu est identique!")
    else:
        print("⚠️  Le contenu diffère")

        # Sauvegarder les deux pour comparaison
        output_dir = Path(__file__).parent

        generated_file = output_dir / "generated_final_json.json"
        with open(generated_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        expected_file = output_dir / "expected_final_json.json"
        with open(expected_file, 'w', encoding='utf-8') as f:
            json.dump(expected_final_json, f, indent=2, ensure_ascii=False)

        print(f"\nFichiers sauvegardés pour comparaison:")
        print(f"  - Généré: {generated_file}")
        print(f"  - Attendu: {expected_file}")
        print(f"\nUtilisez un outil de diff pour comparer:")
        print(f"  diff {generated_file} {expected_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test de la construction incrémentale du final_json")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Comparer avec le résultat attendu au lieu d'afficher les détails"
    )

    args = parser.parse_args()

    if args.compare:
        compare_with_expected()
    else:
        test_incremental_build()
