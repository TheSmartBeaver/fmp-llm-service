"""
Utilitaire pour construire un mapping chemin -> valeur depuis un JSON.

Ce module permet de transformer un JSON hiérarchique en un dictionnaire plat
où chaque clé est un chemin vers une valeur feuille.
"""
from typing import Dict, Any


def build_path_to_value_map(source_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construit un dictionnaire qui mappe chaque chemin concret vers sa valeur.

    Utilise la notation avec indices réels [0], [1], [2]... pour les tableaux.

    Args:
        source_json: Le JSON source avec les données réelles

    Returns:
        Dictionnaire {chemin_concret: valeur}

    Exemple:
        Input: {"metadata": {"course": "Espagnol"}, "items": [{"name": "A"}, {"name": "B"}]}
        Output: {
            "metadata->course": "Espagnol",
            "items[0]->name": "A",
            "items[1]->name": "B"
        }
    """
    path_to_value_map = {}

    def traverse(obj, current_path=""):
        """Traverse récursivement l'objet pour construire le mapping."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}->{key}" if current_path else key

                if isinstance(value, (dict, list)):
                    # Continuer la traversée pour les structures complexes
                    traverse(value, new_path)
                else:
                    # Stocker la valeur feuille
                    path_to_value_map[new_path] = value

        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                # Notation avec index réel: path[0], path[1]...
                new_path = f"{current_path}[{index}]"

                if isinstance(item, (dict, list)):
                    traverse(item, new_path)
                else:
                    # Stocker la valeur feuille
                    path_to_value_map[new_path] = item

    traverse(source_json)
    return path_to_value_map
