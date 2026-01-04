"""
Exemple simple et concret de la fonction _resolve_group_references.

Ce test montre de manière très claire comment les références sont remplacées
avec un exemple minimal et facile à comprendre.
"""

import json
from typing import Any, Dict


def print_section(title: str):
    """Affiche un titre de section."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def resolve_group_references_simple(
    group_jsons_map: Dict[str, Any],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Version simplifiée de _resolve_group_references pour démonstration.
    """
    import re

    def is_group_reference(ref_string: str) -> bool:
        """Vérifie si c'est une référence de groupe."""
        match = re.match(r'^\{\{(.+)\}\}$', ref_string.strip())
        if not match:
            return False
        content = match.group(1)
        return content in group_jsons_map

    def resolve_in_value(value: Any, depth: int = 0, path: str = "") -> Any:
        """Résout récursivement les références."""
        if verbose and depth < 3:  # Limiter l'affichage pour la lisibilité
            indent = "  " * depth

        if isinstance(value, str):
            if is_group_reference(value):
                content = re.match(r'^\{\{(.+)\}\}$', value.strip()).group(1)
                if verbose and depth < 3:
                    print(f"{indent}🔄 Substitution: {value} → groupe '{content}'")
                return group_jsons_map[content]
            return value

        elif isinstance(value, dict):
            return {k: resolve_in_value(v, depth + 1, f"{path}.{k}") for k, v in value.items()}

        elif isinstance(value, list):
            return [resolve_in_value(item, depth + 1, f"{path}[{i}]") for i, item in enumerate(value)]

        else:
            return value

    resolved_map = {}
    for key, group_json in group_jsons_map.items():
        if verbose:
            print(f"\n📦 Traitement du groupe: '{key}'")
        resolved_map[key] = resolve_in_value(group_json, 0, key)

    return resolved_map


def example_1_basic():
    """
    EXEMPLE 1: Substitution basique
    Un template qui référence un autre template.
    """
    print_section("EXEMPLE 1: Substitution basique")

    # Données d'entrée
    group_jsons_map = {
        "titre": {
            "template_name": "text/titre",
            "text": "Mon Titre"
        },
        "section": {
            "template_name": "section",
            "header": "{{titre}}",  # ← Référence au groupe 'titre'
            "content": "Contenu de la section"
        }
    }

    print("📥 INPUT - group_jsons_map:")
    print(json.dumps(group_jsons_map, indent=2, ensure_ascii=False))

    print("\n" + "-" * 80)
    print("🔄 TRAITEMENT:")
    print("-" * 80)

    # Résolution
    resolved = resolve_group_references_simple(group_jsons_map, verbose=True)

    print("\n" + "-" * 80)
    print("📤 OUTPUT - Résultat après résolution:")
    print("-" * 80)
    print()
    print(json.dumps(resolved, indent=2, ensure_ascii=False))

    print("\n💡 Explication:")
    print("   La référence {{titre}} dans le groupe 'section' a été remplacée")
    print("   par la structure JSON complète du groupe 'titre'.")
    print("   Au lieu d'avoir une simple string '{{titre}}', on a maintenant")
    print("   tout l'objet: {\"template_name\": \"text/titre\", \"text\": \"Mon Titre\"}")


def example_2_nested():
    """
    EXEMPLE 2: Substitution avec plusieurs niveaux
    """
    print_section("EXEMPLE 2: Substitution avec plusieurs niveaux")

    group_jsons_map = {
        "label": {
            "template_name": "text/label",
            "text": "Nom:"
        },
        "value": {
            "template_name": "text/value",
            "text": "Jean Dupont"
        },
        "field": {
            "template_name": "layouts/field",
            "label": "{{label}}",      # ← Référence au groupe 'label'
            "value": "{{value}}"       # ← Référence au groupe 'value'
        }
    }

    print("📥 INPUT - group_jsons_map:")
    print(json.dumps(group_jsons_map, indent=2, ensure_ascii=False))

    print("\n" + "-" * 80)
    print("🔄 TRAITEMENT:")
    print("-" * 80)

    resolved = resolve_group_references_simple(group_jsons_map, verbose=True)

    print("\n" + "-" * 80)
    print("📤 OUTPUT - Résultat après résolution:")
    print("-" * 80)
    print()
    print(json.dumps(resolved, indent=2, ensure_ascii=False))

    print("\n💡 Explication:")
    print("   Le groupe 'field' contenait 2 références:")
    print("   - {{label}} → remplacé par le groupe 'label'")
    print("   - {{value}} → remplacé par le groupe 'value'")


def example_3_array():
    """
    EXEMPLE 3: Substitution dans un tableau
    """
    print_section("EXEMPLE 3: Substitution dans un tableau")

    group_jsons_map = {
        "item": {
            "template_name": "text/item",
            "text": "Un élément"
        },
        "liste": {
            "template_name": "layouts/liste",
            "items": [
                "{{item}}",  # ← Référence au groupe 'item'
                "{{item}}",  # ← Référence au groupe 'item'
                "{{item}}"   # ← Référence au groupe 'item'
            ]
        }
    }

    print("📥 INPUT - group_jsons_map:")
    print(json.dumps(group_jsons_map, indent=2, ensure_ascii=False))

    print("\n" + "-" * 80)
    print("🔄 TRAITEMENT:")
    print("-" * 80)

    resolved = resolve_group_references_simple(group_jsons_map, verbose=True)

    print("\n" + "-" * 80)
    print("📤 OUTPUT - Résultat après résolution:")
    print("-" * 80)
    print()
    print(json.dumps(resolved, indent=2, ensure_ascii=False))

    print("\n💡 Explication:")
    print("   Les 3 références {{item}} dans le tableau ont été remplacées")
    print("   par la structure JSON complète du groupe 'item'.")
    print("   Chaque élément du tableau contient maintenant l'objet complet.")


def example_4_recursive():
    """
    EXEMPLE 4: Référence récursive (un groupe qui se référence lui-même)
    """
    print_section("EXEMPLE 4: Référence récursive")

    group_jsons_map = {
        "container": {
            "template_name": "layouts/container",
            "title": "Mon Container",
            "nested": "{{container}}"  # ← Le groupe se référence lui-même!
        }
    }

    print("📥 INPUT - group_jsons_map:")
    print(json.dumps(group_jsons_map, indent=2, ensure_ascii=False))

    print("\n⚠️  ATTENTION: Ce groupe se référence lui-même!")
    print("   La propriété 'nested' contient {{container}}, ce qui crée une référence circulaire.")

    print("\n" + "-" * 80)
    print("🔄 TRAITEMENT:")
    print("-" * 80)

    resolved = resolve_group_references_simple(group_jsons_map, verbose=True)

    print("\n" + "-" * 80)
    print("📤 OUTPUT - Résultat après résolution (tronqué pour lisibilité):")
    print("-" * 80)
    print()
    # Afficher seulement les 2 premiers niveaux
    output = json.dumps(resolved, indent=2, ensure_ascii=False)
    lines = output.split('\n')
    print('\n'.join(lines[:20]))
    if len(lines) > 20:
        print("    ... (structure imbriquée infinie tronquée)")

    print("\n💡 Explication:")
    print("   La référence {{container}} a été remplacée par le groupe 'container',")
    print("   qui contient lui-même une référence {{container}}, et ainsi de suite...")
    print("   Cela crée une structure JSON imbriquée à l'infini.")
    print("   Dans la vraie fonction, il y aurait une limite de profondeur pour éviter cela.")


def main():
    """Fonction principale qui exécute tous les exemples."""
    print(f"\n{'=' * 80}")
    print(f"{'EXEMPLES SIMPLES DE _resolve_group_references':^80}")
    print(f"{'=' * 80}\n")

    print("Ce script montre 4 exemples concrets de la fonction _resolve_group_references.")
    print("Chaque exemple illustre un cas d'usage différent.")

    # Exécuter tous les exemples
    example_1_basic()
    input("\n\n⏸️  Appuyez sur ENTRÉE pour voir l'exemple 2...")

    example_2_nested()
    input("\n\n⏸️  Appuyez sur ENTRÉE pour voir l'exemple 3...")

    example_3_array()
    input("\n\n⏸️  Appuyez sur ENTRÉE pour voir l'exemple 4...")

    example_4_recursive()

    print_section("RÉSUMÉ")

    print("🎯 La fonction _resolve_group_references:")
    print()
    print("  1. Parcourt tous les groupes dans group_jsons_map")
    print("  2. Recherche toutes les références de type {{clé_de_groupe}}")
    print("  3. Remplace chaque référence par la structure JSON complète du groupe correspondant")
    print("  4. Fait cela de manière récursive (une référence peut elle-même contenir d'autres références)")
    print()
    print("📚 Pour voir un test avec des données réelles:")
    print("   python3 tests/test_resolve_group_references_detailed.py")
    print()


if __name__ == "__main__":
    main()
