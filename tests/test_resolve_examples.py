"""
Script qui montre des exemples spécifiques de substitution
pour comprendre visuellement comment _resolve_group_references fonctionne.
"""

import json
from pathlib import Path
from typing import Any, Dict


def print_separator(title: str = ""):
    """Affiche un séparateur avec un titre optionnel."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"{title:^80}")
        print(f"{'=' * 80}\n")
    else:
        print(f"{'-' * 80}\n")


def print_json_pretty(obj: Any, max_depth: int = 3, current_depth: int = 0, indent: str = ""):
    """Affiche un JSON de manière lisible avec coloration."""
    if current_depth > max_depth:
        print(f"{indent}...")
        return

    if isinstance(obj, dict):
        print(f"{indent}{{")
        for i, (key, value) in enumerate(obj.items()):
            is_last = i == len(obj) - 1
            if isinstance(value, (dict, list)):
                print(f"{indent}  \"{key}\": ", end="")
                print_json_pretty(value, max_depth, current_depth + 1, indent + "  ")
                if not is_last:
                    print(f"{indent}  ,")
            else:
                str_value = json.dumps(value, ensure_ascii=False)
                if len(str_value) > 70:
                    str_value = str_value[:67] + "...\"" if str_value.startswith('"') else str_value[:70] + "..."
                comma = "," if not is_last else ""
                print(f"{indent}  \"{key}\": {str_value}{comma}")
        print(f"{indent}}}")
    elif isinstance(obj, list):
        if len(obj) == 0:
            print("[]")
        else:
            print("[")
            for i, item in enumerate(obj[:2]):  # Afficher les 2 premiers
                is_last = i == len(obj) - 1 or i == 1
                print_json_pretty(item, max_depth, current_depth + 1, indent + "  ")
                if not is_last:
                    print(f"{indent}  ,")
            if len(obj) > 2:
                print(f"{indent}  ... ({len(obj)} items total)")
            print(f"{indent}]")
    else:
        str_value = json.dumps(obj, ensure_ascii=False)
        if len(str_value) > 70:
            str_value = str_value[:67] + "...\"" if str_value.startswith('"') else str_value[:70] + "..."
        print(str_value)


def show_substitution_example(
    group_key: str,
    group_jsons_map: Dict[str, Any],
    path_in_group: str,
    reference_value: str
):
    """
    Montre un exemple de substitution spécifique.

    Args:
        group_key: La clé du groupe principal
        group_jsons_map: Le dictionnaire complet des groupes
        path_in_group: Le chemin vers la référence dans le groupe (ex: "title")
        reference_value: La valeur de la référence (ex: "{{summary->title}}")
    """
    print_separator(f"EXEMPLE DE SUBSTITUTION: {group_key}")

    # Extraire la clé de la référence
    ref_key = reference_value.strip("{}").strip()

    print(f"📍 Localisation: {group_key} → {path_in_group}")
    print(f"🔍 Référence trouvée: {reference_value}")
    print(f"🔑 Clé du groupe à substituer: {ref_key}")

    print_separator()

    # Afficher AVANT
    print("AVANT la substitution:")
    print()
    if group_key in group_jsons_map:
        print_json_pretty(group_jsons_map[group_key], max_depth=2)
    print()

    print_separator()

    # Afficher le groupe qui va être substitué
    print(f"Le groupe '{ref_key}' qui va être substitué:")
    print()
    if ref_key in group_jsons_map:
        print_json_pretty(group_jsons_map[ref_key], max_depth=2)
    print()

    print_separator()

    # Simuler l'APRÈS
    print("APRÈS la substitution:")
    print()
    print(f"La valeur '{reference_value}' au chemin '{path_in_group}'")
    print(f"est maintenant remplacée par la structure JSON complète du groupe '{ref_key}'")
    print()
    print("(Voir resolved_output.json pour le résultat complet)")
    print()


def main():
    """Fonction principale."""
    print_separator("EXEMPLES DE SUBSTITUTIONS DE RÉFÉRENCES")

    # Charger les données
    test_dir = Path(__file__).parent / "_resolve_group_references"
    with open(test_dir / "group_jsons_map.json", "r", encoding="utf-8") as f:
        group_jsons_map = json.load(f)

    print(f"✓ Chargé {len(group_jsons_map)} groupes")
    print()

    # Exemple 1: Substitution simple
    show_substitution_example(
        group_key="summary->title",
        group_jsons_map=group_jsons_map,
        path_in_group="title",
        reference_value="{{summary->title}}"
    )

    # Exemple 2: Substitution avec tableau
    show_substitution_example(
        group_key="examplesCollection->examples[x]->notes",
        group_jsons_map=group_jsons_map,
        path_in_group="items[2].text",
        reference_value="{{examplesCollection->examples[x]->notes}}"
    )

    # Exemple 3: Substitution circulaire/récursive
    show_substitution_example(
        group_key="learningStrategies->principles",
        group_jsons_map=group_jsons_map,
        path_in_group="items[1].items[0].items[1].items",
        reference_value="{{learningStrategies->principles}}"
    )

    # Tableau récapitulatif
    print_separator("RÉSUMÉ DES SUBSTITUTIONS")

    print("🔢 Statistiques:")
    print(f"  • Nombre total de groupes: {len(group_jsons_map)}")

    # Compter les références
    total_refs = 0
    for group_key, group_json in group_jsons_map.items():
        refs = count_references(group_json)
        total_refs += refs

    print(f"  • Nombre total de références {{{{...}}}}: {total_refs}")
    print()

    print("📝 Types de substitutions courantes:")
    print()

    examples = [
        {
            "type": "Simple",
            "exemple": "{{course}} → structure JSON du groupe 'course'",
            "description": "Une référence simple vers un autre groupe"
        },
        {
            "type": "Imbriquée",
            "exemple": "{{summary->title}} → structure JSON du groupe 'summary->title'",
            "description": "Référence avec chemin imbriqué"
        },
        {
            "type": "Avec indices",
            "exemple": "{{themes[x]->groups[y]->label}} → structure JSON",
            "description": "Référence avec indices de tableaux"
        },
        {
            "type": "Récursive",
            "exemple": "Un groupe qui référence lui-même",
            "description": "Crée une structure imbriquée infinie (résolu par profondeur max)"
        }
    ]

    for ex in examples:
        print(f"  🔸 {ex['type']}:")
        print(f"     Exemple: {ex['exemple']}")
        print(f"     Description: {ex['description']}")
        print()

    print_separator("FIN DES EXEMPLES")

    print("💡 Pour voir le résultat complet de toutes les substitutions:")
    print("   1. Exécutez: python3 tests/test_resolve_group_references_detailed.py")
    print("   2. Consultez: tests/_resolve_group_references/resolved_output.json")
    print()


def count_references(obj: Any) -> int:
    """Compte le nombre de références {{...}} dans un objet."""
    count = 0

    if isinstance(obj, str):
        if obj.startswith("{{") and obj.endswith("}}"):
            count += 1
    elif isinstance(obj, dict):
        for value in obj.values():
            count += count_references(value)
    elif isinstance(obj, list):
        for item in obj:
            count += count_references(item)

    return count


if __name__ == "__main__":
    main()
