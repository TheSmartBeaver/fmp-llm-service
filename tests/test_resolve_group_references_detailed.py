"""
Test détaillé pour la fonction _resolve_group_references.

Ce test montre comment les références de groupes imbriqués sont résolues
en remplaçant les placeholders {{groupe[x]}} par leurs valeurs JSON correspondantes.
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


def load_test_data():
    """Charge les données de test depuis les fichiers JSON."""
    test_dir = Path(__file__).parent / "_resolve_group_references"

    with open(test_dir / "group_jsons_map.json", "r", encoding="utf-8") as f:
        group_jsons_map = json.load(f)

    with open(test_dir / "path_to_value_map.json", "r", encoding="utf-8") as f:
        path_to_value_map = json.load(f)

    return group_jsons_map, path_to_value_map


def print_json_structure(obj: Any, indent: int = 0, max_depth: int = 3) -> None:
    """Affiche la structure d'un objet JSON de manière lisible."""
    prefix = "  " * indent

    if indent > max_depth:
        print(f"{prefix}...")
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                print_json_structure(value, indent + 1, max_depth)
            else:
                # Tronquer les longues valeurs
                str_value = str(value)
                if len(str_value) > 80:
                    str_value = str_value[:77] + "..."
                print(f"{prefix}{key}: {str_value}")
    elif isinstance(obj, list):
        if len(obj) == 0:
            print(f"{prefix}[]")
        else:
            for i, item in enumerate(obj[:3]):  # Afficher seulement les 3 premiers
                print(f"{prefix}[{i}]:")
                print_json_structure(item, indent + 1, max_depth)
            if len(obj) > 3:
                print(f"{prefix}... ({len(obj)} items total)")
    else:
        str_value = str(obj)
        if len(str_value) > 80:
            str_value = str_value[:77] + "..."
        print(f"{prefix}{str_value}")


def find_all_references(obj: Any, path: str = "") -> Dict[str, str]:
    """
    Trouve toutes les références {{...}} dans un objet JSON.

    Returns:
        Dict avec {chemin_complet: valeur_de_reference}
    """
    references = {}

    if isinstance(obj, str):
        if obj.startswith("{{") and obj.endswith("}}"):
            references[path] = obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            references.update(find_all_references(value, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            references.update(find_all_references(item, new_path))

    return references


def simulate_resolve_group_references(
    group_jsons_map: Dict[str, Dict[str, Any]],
    path_to_value_map: Dict[str, Any],
    verbose: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Simule la fonction _resolve_group_references avec affichage détaillé.

    Cette fonction reproduit le comportement de _resolve_group_references
    mais avec des affichages détaillés pour voir chaque étape de substitution.
    """
    import re

    if verbose:
        print("=" * 80)
        print("DÉBUT DE LA RÉSOLUTION DES RÉFÉRENCES DE GROUPES")
        print("=" * 80)
        print()

    def is_group_reference(ref_string: str) -> bool:
        """Vérifie si une string de référence {{...}} pointe vers un groupe."""
        match = re.match(r'^\{\{(.+)\}\}$', ref_string.strip())
        if not match:
            return False
        content = match.group(1)
        return content in group_jsons_map

    substitution_count = 0
    substitution_details = []

    def resolve_in_value(value: Any, current_path: str = "") -> Any:
        """Résout récursivement les références dans une valeur."""
        nonlocal substitution_count

        if isinstance(value, str):
            # Vérifier si c'est une référence de groupe
            if is_group_reference(value):
                # Extraire le contenu entre {{ et }}
                content = re.match(r'^\{\{(.+)\}\}$', value.strip()).group(1)

                # Retourner directement le JSON du groupe
                if content in group_jsons_map:
                    substitution_count += 1

                    # Enregistrer les détails de la substitution
                    substitution_details.append({
                        "numero": substitution_count,
                        "localisation": current_path,
                        "reference": value,
                        "cle_groupe": content,
                        "avant": value,
                        "apres_type": type(group_jsons_map[content]).__name__,
                        "apres_preview": str(group_jsons_map[content])[:100] + "..."
                                       if len(str(group_jsons_map[content])) > 100
                                       else str(group_jsons_map[content])
                    })

                    return group_jsons_map[content]

            return value

        elif isinstance(value, dict):
            # Résoudre récursivement dans les dictionnaires
            return {k: resolve_in_value(v, f"{current_path}.{k}" if current_path else k)
                    for k, v in value.items()}

        elif isinstance(value, list):
            # Résoudre récursivement dans les listes
            return [resolve_in_value(item, f"{current_path}[{i}]")
                    for i, item in enumerate(value)]

        else:
            return value

    # Analyse préliminaire: compter toutes les références
    if verbose:
        print("ÉTAPE 1: ANALYSE DES RÉFÉRENCES")
        print("-" * 80)
        total_references = 0
        for key, group_json in group_jsons_map.items():
            refs = find_all_references(group_json)
            if refs:
                total_references += len(refs)

        print(f"Nombre total de groupes dans group_jsons_map: {len(group_jsons_map)}")
        print(f"Nombre total de références {{...}} trouvées: {total_references}")
        print()

    # Résoudre les références dans tous les groupes
    if verbose:
        print("ÉTAPE 2: RÉSOLUTION DES RÉFÉRENCES")
        print("-" * 80)

    resolved_map = {}
    for key, group_json in group_jsons_map.items():
        if verbose:
            print(f"\nTraitement du groupe: '{key}'")
            print(f"  Type: {type(group_json).__name__}")

        # Compter les références dans ce groupe avant résolution
        refs_before = find_all_references(group_json)
        if verbose and refs_before:
            print(f"  Références trouvées: {len(refs_before)}")
            for ref_path, ref_value in list(refs_before.items())[:5]:  # Afficher les 5 premières
                print(f"    - {ref_path}: {ref_value}")
            if len(refs_before) > 5:
                print(f"    ... et {len(refs_before) - 5} autres")

        # Résoudre
        resolved_value = resolve_in_value(group_json, key)
        resolved_map[key] = resolved_value

        # Afficher le JSON construit après résolution
        if verbose:
            print(f"\n  {'=' * 76}")
            print(f"  JSON CONSTRUIT pour '{key}':")
            print(f"  {'=' * 76}")
            print(json.dumps(resolved_value, indent=2, ensure_ascii=False))
            print(f"  {'=' * 76}")

    # Afficher le résumé des substitutions
    if verbose:
        print()
        print("=" * 80)
        print("ÉTAPE 3: RÉSUMÉ DES SUBSTITUTIONS")
        print("=" * 80)
        print(f"\nNombre total de substitutions effectuées: {substitution_count}")
        print()

        if substitution_details:
            print("Détail de chaque substitution:")
            print()
            for detail in substitution_details:
                print(f"Substitution #{detail['numero']}:")
                print(f"  Localisation: {detail['localisation']}")
                print(f"  Référence: {detail['reference']}")
                print(f"  Clé du groupe: {detail['cle_groupe']}")
                print(f"  AVANT: {detail['avant']}")
                print(f"  APRÈS (type): {detail['apres_type']}")
                print(f"  APRÈS (aperçu): {detail['apres_preview']}")
                print()

    # Vérification des clés (comme dans la fonction originale)
    if verbose:
        print("=" * 80)
        print("ÉTAPE 4: VÉRIFICATION DES CLÉS")
        print("=" * 80)

    def extract_all_keys(obj, keys_set=None):
        """Extrait toutes les clés présentes dans resolved_map (récursivement)."""
        if keys_set is None:
            keys_set = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key != "items":  # Ne pas ajouter "items" comme clé
                    keys_set.add(key)
                # Descendre récursivement même si c'est "items"
                extract_all_keys(value, keys_set)
        elif isinstance(obj, list):
            for item in obj:
                extract_all_keys(item, keys_set)

        return keys_set

    # Extraire toutes les clés de resolved_map
    resolved_keys = extract_all_keys(resolved_map)

    # Pour simplifier, on compare avec les clés de path_to_value_map
    # (normalisation simplifiée)
    def normalize_path(path: str) -> str:
        """Normalise un chemin en remplaçant les indices spécifiques par [x], [y], [z]."""
        import re
        # Remplacer [0] par [x], [1] par [y], etc. (simplifié)
        path = re.sub(r'\[0\]', '[x]', path)
        path = re.sub(r'\[1\]', '[y]', path)
        path = re.sub(r'\[2\]', '[z]', path)
        path = re.sub(r'\[\d+\]', '[x]', path)  # Autres indices deviennent [x]
        return path

    required_keys = {normalize_path(path.split('->')[-1]) for path in path_to_value_map.keys()}

    if verbose:
        print(f"\nNombre de clés requises (de path_to_value_map): {len(required_keys)}")
        print(f"Nombre de clés présentes (dans resolved_map): {len(resolved_keys)}")

        # Trouver les clés manquantes
        missing_keys = required_keys - resolved_keys
        if missing_keys:
            print(f"\n⚠️  AVERTISSEMENT: {len(missing_keys)} clés manquantes:")
            for key in sorted(list(missing_keys)[:10]):  # Afficher les 10 premières
                print(f"   - {key}")
            if len(missing_keys) > 10:
                print(f"   ... et {len(missing_keys) - 10} autres")
            print(f"\nTaux de couverture: {((len(required_keys) - len(missing_keys)) / len(required_keys) * 100):.1f}%")
        else:
            print("\n✓ Toutes les clés requises sont présentes!")

    if verbose:
        print()
        print("=" * 80)
        print("FIN DE LA RÉSOLUTION")
        print("=" * 80)
        print()

    return resolved_map


def test_resolve_group_references():
    """
    Test principal qui montre toutes les étapes de résolution.
    """
    print("\n" + "=" * 80)
    print("TEST: _resolve_group_references")
    print("=" * 80)
    print()

    # Charger les données de test
    print("Chargement des données de test...")
    group_jsons_map, path_to_value_map = load_test_data()

    print(f"✓ group_jsons_map chargé: {len(group_jsons_map)} groupes")
    print(f"✓ path_to_value_map chargé: {len(path_to_value_map)} chemins")
    print()

    # Afficher quelques exemples de groupes avant résolution
    print("=" * 80)
    print("APERÇU DES DONNÉES AVANT RÉSOLUTION")
    print("=" * 80)
    print()

    print("Exemples de groupes dans group_jsons_map:")
    print()

    # Montrer 3 exemples intéressants
    example_keys = [
        "summary->title",
        "themes[x]->examples[y]->conjugation[z]->meaning",
        "examplesCollection->examples[x]->notes"
    ]

    for key in example_keys:
        if key in group_jsons_map:
            print(f"Groupe: '{key}'")
            print_json_structure(group_jsons_map[key], max_depth=2)
            print()

    # Afficher quelques exemples de path_to_value_map
    print("Exemples de valeurs dans path_to_value_map:")
    print()
    for i, (path, value) in enumerate(list(path_to_value_map.items())[:5]):
        str_value = str(value)
        if len(str_value) > 100:
            str_value = str_value[:97] + "..."
        print(f"  {path}: {str_value}")
    print(f"  ... et {len(path_to_value_map) - 5} autres")
    print()

    # Exécuter la résolution avec affichage détaillé
    resolved_map = simulate_resolve_group_references(
        group_jsons_map,
        path_to_value_map,
        verbose=True
    )

    # Afficher quelques exemples après résolution
    print("=" * 80)
    print("APERÇU DES DONNÉES APRÈS RÉSOLUTION")
    print("=" * 80)
    print()

    for key in example_keys[:2]:  # Afficher 2 exemples
        if key in resolved_map:
            print(f"Groupe résolu: '{key}'")
            print_json_structure(resolved_map[key], max_depth=2)
            print()

    # Sauvegarder le résultat dans un fichier pour inspection
    output_path = Path(__file__).parent / "_resolve_group_references" / "resolved_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resolved_map, f, indent=2, ensure_ascii=False)

    print(f"✓ Résultat complet sauvegardé dans: {output_path}")
    print()

    print("=" * 80)
    print("TEST TERMINÉ")
    print("=" * 80)


if __name__ == "__main__":
    test_resolve_group_references()
