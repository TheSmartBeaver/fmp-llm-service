def extract_json_structure(data):
    """
    Extrait la structure d'un JSON en cartographiant tous les chemins de clés.

    - Les valeurs primitives sont remplacées par leur type ("string", "number", "boolean", "null")
    - Les arrays conservent un élément représentatif fusionnant toutes les clés possibles
    - Les objets imbriqués sont traités récursivement

    Args:
        data: Le JSON à analyser (dict, list, ou valeur primitive)

    Returns:
        La structure du JSON avec les types au lieu des valeurs

    Example:
        >>> json_data = {
        ...     "name": "John",
        ...     "age": 30,
        ...     "items": [
        ...         {"id": 1, "type": "A"},
        ...         {"id": 2, "category": "B"}
        ...     ]
        ... }
        >>> extract_json_structure(json_data)
        {
            "name": "string",
            "age": "number",
            "items": [
                {
                    "id": "number",
                    "type": "string",
                    "category": "string"
                }
            ]
        }
    """
    if data is None:
        return "null"

    elif isinstance(data, bool):
        # bool doit être testé AVANT int car bool est une sous-classe de int en Python
        return "boolean"

    elif isinstance(data, (int, float)):
        return "number"

    elif isinstance(data, str):
        return "string"

    elif isinstance(data, list):
        if len(data) == 0:
            return []

        # Fusionner toutes les structures des éléments du tableau
        merged_structure = None

        for item in data:
            item_structure = extract_json_structure(item)

            if merged_structure is None:
                merged_structure = item_structure
            else:
                # Fusionner les structures (uniquement pour les objets)
                if isinstance(merged_structure, dict) and isinstance(item_structure, dict):
                    merged_structure = merge_structures(merged_structure, item_structure)

        return [merged_structure] if merged_structure is not None else []

    elif isinstance(data, dict):
        return {key: extract_json_structure(value) for key, value in data.items()}

    else:
        # Type inconnu, retourner une représentation string
        return "unknown"


def merge_structures(struct1, struct2):
    """
    Fusionne deux structures d'objets en combinant toutes les clés possibles.

    Args:
        struct1: Première structure (dict)
        struct2: Deuxième structure (dict)

    Returns:
        Structure fusionnée contenant toutes les clés des deux structures
    """
    if not isinstance(struct1, dict) or not isinstance(struct2, dict):
        # Si l'un des deux n'est pas un dict, retourner struct2 (ou struct1)
        return struct2 if struct2 is not None else struct1

    merged = struct1.copy()

    for key, value2 in struct2.items():
        if key in merged:
            value1 = merged[key]

            # Si les deux valeurs sont des dicts, les fusionner récursivement
            if isinstance(value1, dict) and isinstance(value2, dict):
                merged[key] = merge_structures(value1, value2)

            # Si les deux valeurs sont des listes avec des dicts, fusionner les structures
            elif isinstance(value1, list) and isinstance(value2, list):
                if len(value1) > 0 and len(value2) > 0:
                    if isinstance(value1[0], dict) and isinstance(value2[0], dict):
                        merged[key] = [merge_structures(value1[0], value2[0])]
                    else:
                        # Garder value2 (ou value1, peu importe si ce sont des primitives)
                        merged[key] = value2
                elif len(value2) > 0:
                    merged[key] = value2

            # Sinon, garder value2 (la nouvelle valeur écrase l'ancienne)
            else:
                merged[key] = value2
        else:
            # Nouvelle clé, l'ajouter
            merged[key] = value2

    return merged


def create_embedding_packets(data):
    """
    Crée des paquets de texte pour générer plusieurs embeddings ciblés.

    Stratégie:
    - Paquet 1: Toutes les clés de niveau racine et niveau 1 (structure macro)
    - Paquets 2+: Groupes de champs terminaux (feuilles) regroupés par leur parent (structure micro)

    Args:
        data: Le JSON source

    Returns:
        Liste de paquets, chacun contenant:
        - type: "macro" ou "micro"
        - keys: liste des clés/chemins
        - text: texte formaté pour l'embedding
        - context: chemin parent (pour paquets micro)

    Example:
        >>> json_data = {
        ...     "structure": {
        ...         "sujet_principal": "string",
        ...         "archeologie_moleculaire": {
        ...             "etude_de_cas_chine": {
        ...                 "chercheur": "string",
        ...                 "objet_etude": "string"
        ...             }
        ...         },
        ...         "chronologie_historique": [
        ...             {
        ...                 "periode": "string",
        ...                 "evenement": "string"
        ...             }
        ...         ]
        ...     }
        ... }
        >>> packets = create_embedding_packets(json_data)
        >>> packets[0]["type"]
        'macro'
        >>> "sujet_principal" in packets[0]["keys"]
        True
    """
    structure = extract_json_structure(data)
    packets = []

    # PAQUET 1: Clés macro (niveau racine + niveau 1)
    macro_keys = _extract_macro_keys(structure, max_depth=2)
    if macro_keys:
        packets.append({
            "type": "macro",
            "keys": macro_keys,
            "text": " ".join(macro_keys),
            "context": ""
        })

    # PAQUETS 2+: Groupes de champs feuilles par parent
    micro_packets = _extract_micro_packets(structure)
    packets.extend(micro_packets)

    return packets


def _extract_macro_keys(obj, current_depth=0, max_depth=2):
    """
    Extrait les clés de haut niveau jusqu'à une profondeur maximale.

    Args:
        obj: L'objet JSON structuré
        current_depth: Profondeur actuelle
        max_depth: Profondeur maximale à explorer

    Returns:
        Liste des clés de haut niveau
    """
    keys = []

    if current_depth >= max_depth:
        return keys

    if isinstance(obj, dict):
        for key in obj.keys():
            keys.append(key)
            # Récursion pour aller plus profond
            sub_keys = _extract_macro_keys(obj[key], current_depth + 1, max_depth)
            keys.extend(sub_keys)

    elif isinstance(obj, list) and len(obj) > 0:
        # Pour les tableaux, explorer le premier élément
        sub_keys = _extract_macro_keys(obj[0], current_depth, max_depth)
        keys.extend(sub_keys)

    return keys


def _extract_micro_packets(obj, path="", packets=None):
    """
    Extrait les paquets de champs feuilles regroupés par leur parent.

    Un "parent groupant" est:
    - Un objet contenant principalement des valeurs primitives
    - Le premier élément d'un tableau d'objets

    Args:
        obj: L'objet JSON structuré
        path: Chemin actuel
        packets: Liste accumulée des paquets

    Returns:
        Liste des paquets micro
    """
    if packets is None:
        packets = []

    if isinstance(obj, dict):
        # Vérifier si cet objet contient principalement des feuilles (primitives)
        leaf_keys = []
        complex_children = []

        for key, value in obj.items():
            if isinstance(value, str):  # C'est un type ("string", "number", etc.)
                leaf_keys.append(key)
            else:
                complex_children.append((key, value))

        # Si on a des feuilles ET que c'est un groupe significatif (2+ champs)
        if len(leaf_keys) >= 2:
            # Créer un paquet pour ces feuilles
            packets.append({
                "type": "micro",
                "keys": leaf_keys,
                "text": " ".join(leaf_keys),
                "context": path
            })

        # Continuer la récursion pour les enfants complexes
        for key, value in complex_children:
            new_path = f"{path}->{key}" if path else key
            _extract_micro_packets(value, new_path, packets)

    elif isinstance(obj, list) and len(obj) > 0:
        # Pour les tableaux, analyser le premier élément (structure fusionnée)
        item = obj[0]

        if isinstance(item, dict):
            # Extraire les clés feuilles du premier élément
            leaf_keys = [k for k, v in item.items() if isinstance(v, str)]

            if len(leaf_keys) >= 2:
                # Créer un paquet pour les champs du tableau
                array_path = f"{path}[]" if path else "[]"
                packets.append({
                    "type": "micro",
                    "keys": leaf_keys,
                    "text": " ".join(leaf_keys),
                    "context": array_path
                })

            # Récursion pour les champs complexes dans le tableau
            for key, value in item.items():
                if not isinstance(value, str):
                    new_path = f"{path}[]{key}" if path else f"[]{key}"
                    _extract_micro_packets(value, new_path, packets)

    return packets


# Exemple d'utilisation
if __name__ == "__main__":
    import json

    # Exemple de JSON d'entrée
    sample_json = {
        "course_title": "Mini cours d'espagnol – Apprendre la conjugaison",
        "learning_objective": "Maîtriser la conjugaison des verbes espagnols réguliers",
        "course_sections": [
            {
                "section_id": "general_rules",
                "section_type": "theory",
                "section_title": "Règles générales",
                "description": "En espagnol, les verbes se terminent par -ar, -er ou -ir."
            },
            {
                "section_id": "regular_verbs_conjugation_tables",
                "section_type": "conjugation_tables",
                "section_title": "Verbes réguliers au présent de l'indicatif",
                "tables": [
                    {
                        "verb_group": "-ar",
                        "infinitive": "hablar",
                        "infinitive_translation": "parler",
                        "conjugation_table": [
                            {
                                "pronoun_es": "yo",
                                "verb_form": "hablo",
                                "translation_fr": "je parle"
                            }
                        ]
                    }
                ]
            },
            {
                "section_id": "learning_tips",
                "section_type": "study_tips",
                "section_title": "Conseils pour progresser",
                "tips": [
                    "Mémoriser un verbe modèle par groupe (-ar, -er, -ir).",
                    "Lire les tables en associant systématiquement la forme espagnole"
                ]
            }
        ]
    }

    # Extraire la structure
    structure = extract_json_structure(sample_json)

    # Afficher le résultat formaté
    print(json.dumps(structure, indent=2, ensure_ascii=False))
