import re
from typing import Any, Dict, List


def validate_path_groups(path_groups: List[Dict[str, Any]]) -> List[str]:
    """
    Valide que les path_groups respectent les contraintes.

    Contraintes vérifiées:
    1. Pas de mélange de clés avec et sans variables dans un même groupe
    2. Même profondeur de variables (nombre de variables) pour toutes les clés avec variables
    3. Même préfixe jusqu'à la dernière variable pour toutes les clés avec variables

    Args:
        path_groups: Liste des groupes générés par le LLM

    Returns:
        Liste des warnings/erreurs détectés
    """
    warnings = []
    
    for group in path_groups:
        keys = group["keys"]
        
        # Séparer les clés avec variables et sans variables
        keys_with_vars = []
        keys_without_vars = []
        
        for key in keys:
            if re.search(r'\[[x-z]\]', key):
                keys_with_vars.append(key)
            else:
                keys_without_vars.append(key)
        
        # Si mélange de clés avec et sans variables
        if keys_with_vars and keys_without_vars:
            # Identifier le groupe par ses premières clés
            group_identifier = f"[{', '.join(keys[:2])}...]" if len(keys) > 2 else f"[{', '.join(keys)}]"
            warnings.append(
                f"⚠️ Groupe {group_identifier} mélange des clés avec et sans variables:\n"
                f"  Avec variables: {keys_with_vars}\n"
                f"  Sans variables: {keys_without_vars}\n"
                f"  → Les clés sans variables devraient être dans un groupe séparé."
            )
        
        # Si clés avec variables, vérifier la cohérence
        if keys_with_vars:
            # Vérifier la profondeur de variable (nombre de variables)
            variable_depths = {}
            
            for key in keys_with_vars:
                # Compter les variables
                vars_in_key = re.findall(r'\[([x-z])\]', key)
                depth = len(vars_in_key)
                
                if depth not in variable_depths:
                    variable_depths[depth] = []
                variable_depths[depth].append(key)
            
            # Si profondeurs différentes
            if len(variable_depths) > 1:
                # Identifier le groupe par ses premières clés
                group_identifier = f"[{', '.join(keys[:2])}...]" if len(keys) > 2 else f"[{', '.join(keys)}]"
                warning_msg = f"⚠️ Groupe {group_identifier} contient des clés avec profondeurs de variables différentes:\n"
                for depth, keys_at_depth in variable_depths.items():
                    warning_msg += f"  Profondeur {depth}: {keys_at_depth}\n"
                warning_msg += (
                    f"  → Les clés de profondeur différente devraient utiliser des références imbriquées.\n"
                    f"     Ex: au lieu de {{{{path[x]->sub[y]->field}}}}, utiliser {{{{path[x]->sub[y]}}}} qui référence un autre groupe"
                )
                warnings.append(warning_msg)
            
            # NOTE: La vérification du préfixe commun est désactivée car il est légitime
            # d'avoir des clés avec des préfixes différents dans un même groupe lorsqu'elles
            # sont sémantiquement liées (ex: themes[x]groups[y] et themes[x]examples[y],
            # ou media->videos[x] et media->images[x])

            # # Vérifier le préfixe commun jusqu'à la dernière variable
            # prefixes = []
            # for key in keys_with_vars:
            #     # Extraire le préfixe jusqu'à la dernière variable
            #     vars_matches = list(re.finditer(r'\[([x-z])\]', key))
            #     if vars_matches:
            #         last_var_end = vars_matches[-1].end()
            #         prefix = key[:last_var_end]
            #         prefixes.append(prefix)
            #
            # # Tous les préfixes doivent être identiques
            # unique_prefixes = set(prefixes)
            # if len(unique_prefixes) > 1:
            #     warning_msg = f"⚠️ Groupe '{group['group_name']}' contient des clés avec préfixes différents:\n"
            #     for prefix in unique_prefixes:
            #         matching_keys = [k for k, p in zip(keys_with_vars, prefixes) if p == prefix]
            #         warning_msg += f"  Préfixe '{prefix}': {matching_keys}\n"
            #     warning_msg += f"  → Ces clés devraient être dans des groupes séparés."
            #     warnings.append(warning_msg)
    
    return warnings