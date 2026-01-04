"""
Module pour construire le final_json de manière incrémentale à partir de entry et group_jsons_map.

Cet algorithme parcourt entry une seule fois et construit progressivement le final_json
en utilisant les templates de group_jsons_map et en résolvant les placeholders.
"""

import re
import copy
import json
from typing import Any, Dict, List, Tuple


def convert_indices_to_variables(path_with_indices: str) -> Tuple[str, Dict[str, int]]:
    """
    Convertit un chemin avec indices en chemin avec variables.

    Args:
        path_with_indices: Chemin avec indices réels (ex: "themes[0]->groups[1]->label")

    Returns:
        Tuple de (chemin_avec_variables, mapping_variables)
        Ex: ("themes[x]->groups[y]->label", {"x": 0, "y": 1})
    """
    var_mapping = {}
    var_names = ['x', 'y', 'z', 'w', 'v', 'u', 't', 's', 'r', 'q']
    var_index = 0

    def replace_index(match):
        nonlocal var_index
        index_value = int(match.group(1))
        var_name = var_names[var_index]
        var_mapping[var_name] = index_value
        var_index += 1
        return f"[{var_name}]"

    # Remplacer tous les [nombre] par [variable]
    path_with_vars = re.sub(r'\[(\d+)\]', replace_index, path_with_indices)

    return path_with_vars, var_mapping


def find_all_placeholders(obj: Any) -> List[str]:
    """
    Trouve tous les placeholders {{...}} dans un objet JSON (récursif).

    Args:
        obj: Objet JSON (dict, list, str, etc.)

    Returns:
        Liste de tous les placeholders trouvés
    """
    placeholders = []

    if isinstance(obj, str):
        # Chercher tous les {{...}} dans la chaîne
        matches = re.findall(r'\{\{[^}]+\}\}', obj)
        placeholders.extend(matches)
    elif isinstance(obj, dict):
        for value in obj.values():
            placeholders.extend(find_all_placeholders(value))
    elif isinstance(obj, list):
        for item in obj:
            placeholders.extend(find_all_placeholders(item))

    return placeholders


def extract_path(placeholder: str) -> str:
    """
    Extrait le chemin à l'intérieur d'un placeholder.

    Args:
        placeholder: Placeholder (ex: "{{themes[x]->groups[y]->label}}")

    Returns:
        Chemin extrait (ex: "themes[x]->groups[y]->label")
    """
    # Enlever {{ et }}
    return placeholder.strip('{}').strip()


def substitute_variables(path: str, var_mapping: Dict[str, int]) -> str:
    """
    Substitue les variables par leurs valeurs dans un chemin.

    Args:
        path: Chemin avec variables (ex: "themes[x]->groups[y]->label")
        var_mapping: Mapping des variables (ex: {"x": 0, "y": 1})

    Returns:
        Chemin avec indices réels (ex: "themes[0]->groups[1]->label")
    """
    result = path
    for var_name, index_value in var_mapping.items():
        result = result.replace(f"[{var_name}]", f"[{index_value}]")
    return result


def replace_in_template(obj: Any, placeholder: str, value: Any) -> Any:
    """
    Remplace toutes les occurrences d'un placeholder par une valeur dans un objet (récursif, in-place).

    Args:
        obj: Objet JSON à modifier
        placeholder: Placeholder à remplacer (ex: "{{themes[0]->groups[1]->label}}")
        value: Valeur de remplacement

    Returns:
        Objet modifié (modification in-place)
    """
    if isinstance(obj, str):
        # Si la chaîne EST exactement le placeholder, on retourne la valeur
        if obj == placeholder:
            return value
        # Sinon on remplace le placeholder dans la chaîne
        return obj.replace(placeholder, str(value))
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = replace_in_template(obj[key], placeholder, value)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_in_template(obj[i], placeholder, value)

    return obj


def build_final_json_incremental(
    entry: Dict[str, Any],
    group_jsons_map: Dict[str, Any],
    verbose: bool = True
) -> List[Any]:
    """
    Construit le final_json de manière incrémentale à partir de entry et group_jsons_map.

    Args:
        entry: Dictionnaire plat avec chemins -> valeurs
        group_jsons_map: Dictionnaire avec chemins (avec variables) -> templates JSON
        verbose: Si True, affiche les logs de progression

    Returns:
        Liste de templates JSON résolus (final_json)
    """
    final_json = []
    templates_seen = {}  # Cache: (template_id, var_mapping_tuple) -> template_instance
    template_ids = {}    # Cache: path_with_vars -> template_id (hash du template JSON)

    total_paths = len(entry)
    processed = 0

    if verbose:
        print("=" * 80)
        print("CONSTRUCTION INCRÉMENTALE DU FINAL_JSON")
        print("=" * 80)
        print(f"Total de chemins à traiter: {total_paths}\n")

    for path_with_indices, value in entry.items():
        processed += 1

        if verbose:
            print(f"\n[{processed}/{total_paths}] Traitement: {path_with_indices}")
            print(f"  Valeur: {value if len(str(value)) < 80 else str(value)[:77] + '...'}")

        # ÉTAPE 1: Convertir indices → variables
        path_with_vars, var_mapping = convert_indices_to_variables(path_with_indices)

        if verbose:
            print(f"  Chemin avec variables: {path_with_vars}")
            if var_mapping:
                print(f"  Mapping des variables: {var_mapping}")

        # ÉTAPE 2: Chercher le template correspondant
        if path_with_vars not in group_jsons_map:
            if verbose:
                print(f"  ⊘ SKIP: Aucun template trouvé pour '{path_with_vars}'")
            continue

        template = group_jsons_map[path_with_vars]

        # ÉTAPE 2.5: Identifier le template de manière unique (par son contenu JSON)
        # Si plusieurs chemins pointent vers le même template (même structure),
        # ils doivent partager la même instance
        if path_with_vars not in template_ids:
            template_id = json.dumps(template, sort_keys=True)
            template_ids[path_with_vars] = template_id
        else:
            template_id = template_ids[path_with_vars]

        # ÉTAPE 3: Vérifier si on doit créer une nouvelle instance ou réutiliser
        # La clé de cache combine le template_id ET les indices des variables
        cache_key = (template_id, tuple(sorted(var_mapping.items())))

        if cache_key in templates_seen:
            # Réutiliser l'instance existante
            template_instance = templates_seen[cache_key]
            if verbose:
                print(f"  ♻️  Réutilisation du template existant")
        else:
            # Créer une nouvelle instance
            template_instance = copy.deepcopy(template)
            templates_seen[cache_key] = template_instance
            final_json.append(template_instance)
            if verbose:
                print(f"  ✓ Nouveau template créé et ajouté à final_json (position {len(final_json) - 1})")

        # ÉTAPE 4: Transformer les variables en indices réels dans les placeholders
        # On ne résout PAS les placeholders, on remplace juste x,y,z par les indices réels
        if var_mapping:
            placeholders = find_all_placeholders(template_instance)

            if verbose and placeholders:
                print(f"  Placeholders trouvés: {len(placeholders)} - substitution des variables...")

            for placeholder in placeholders:
                # Extraire le chemin du placeholder
                placeholder_path = extract_path(placeholder)

                # Substituer les variables par les indices réels
                resolved_path = substitute_variables(placeholder_path, var_mapping)

                # Créer le nouveau placeholder avec indices réels
                new_placeholder = "{{" + resolved_path + "}}"

                # Remplacer l'ancien placeholder par le nouveau
                replace_in_template(template_instance, placeholder, new_placeholder)

                if verbose:
                    print(f"    • {placeholder} → {new_placeholder}")

        # ÉTAPE 5: Affichage incrémental
        if verbose:
            print(f"\n  📦 Taille actuelle de final_json: {len(final_json)} templates")

    if verbose:
        print("\n" + "=" * 80)
        print(f"✅ CONSTRUCTION TERMINÉE: {len(final_json)} templates créés")
        print("=" * 80)

    return final_json


def print_json_preview(obj: Any, max_depth: int = 2, current_depth: int = 0, indent: str = ""):
    """
    Affiche un aperçu limité d'un objet JSON.

    Args:
        obj: Objet à afficher
        max_depth: Profondeur maximale d'affichage
        current_depth: Profondeur actuelle (usage interne)
        indent: Indentation actuelle (usage interne)
    """
    if current_depth >= max_depth:
        if isinstance(obj, dict):
            print(f"{indent}{{...}} ({len(obj)} clés)")
        elif isinstance(obj, list):
            print(f"{indent}[...] ({len(obj)} éléments)")
        else:
            value_str = str(obj)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            print(f"{indent}{value_str}")
        return

    if isinstance(obj, dict):
        print(f"{indent}{{")
        for i, (key, value) in enumerate(obj.items()):
            print(f"{indent}  {key}: ", end="")
            if isinstance(value, (dict, list)):
                print()
                print_json_preview(value, max_depth, current_depth + 1, indent + "    ")
            else:
                value_str = str(value)
                if len(value_str) > 60:
                    value_str = value_str[:57] + "..."
                print(value_str)
            if i < len(obj) - 1:
                print(f"{indent}  ,")
        print(f"{indent}}}")
    elif isinstance(obj, list):
        print(f"{indent}[")
        for i, item in enumerate(obj):
            print_json_preview(item, max_depth, current_depth + 1, indent + "  ")
            if i < len(obj) - 1:
                print(f"{indent}  ,")
        print(f"{indent}]")
    else:
        value_str = str(obj)
        if len(value_str) > 60:
            value_str = value_str[:57] + "..."
        print(f"{indent}{value_str}")
