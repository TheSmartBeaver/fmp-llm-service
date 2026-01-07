"""
Fonctions utilitaires pour le système de corrections.
"""

from typing import Any, Set, Union, Dict, List, Tuple
import logging

from app.chains.correctors.corrector_registry import CorrectorRegistry
from app.chains.correctors.correction_queue import CorrectionQueue


def extract_template_names(obj: Any) -> Set[str]:
    """
    Extrait récursivement tous les template_name présents dans la structure.

    Parcourt la structure JSON (dict/list) et collecte tous les
    champs "template_name" rencontrés.

    Args:
        obj: Structure JSON (dict, list ou autre type)

    Returns:
        Set de tous les template_name trouvés

    Examples:
        >>> data = {
        ...     "template_name": "layouts/container",
        ...     "items": [
        ...         {"template_name": "text/title", "text": "Hello"}
        ...     ]
        ... }
        >>> extract_template_names(data)
        {'layouts/container', 'text/title'}
    """
    template_names = set()

    if isinstance(obj, dict):
        # Si c'est un dict avec template_name, l'ajouter
        if "template_name" in obj:
            template_names.add(obj["template_name"])

        # Parcourir récursivement toutes les valeurs
        for value in obj.values():
            template_names.update(extract_template_names(value))

    elif isinstance(obj, list):
        # Parcourir récursivement tous les items
        for item in obj:
            template_names.update(extract_template_names(item))

    return template_names


def processSeriesOfCorrections(
    template_structure: Union[Dict, List],
    registry: CorrectorRegistry,
    max_iterations: int = 10,
) -> Tuple[Union[Dict, List], Dict[str, Any]]:
    """
    Applique une série de corrections sur la structure de templates.

    Processus:
    1. Extraire tous les template_name présents dans la structure
    2. Récupérer les correcteurs applicables du registre
    3. Créer une CorrectionQueue avec ces correcteurs
    4. Appliquer les corrections en boucle jusqu'à stabilisation
    5. Retourner la structure corrigée + statistiques

    Args:
        template_structure: Structure JSON à corriger
        registry: Registre contenant tous les correcteurs disponibles
        max_iterations: Nombre max d'itérations (défaut: 10)

    Returns:
        Tuple contenant:
        - Structure corrigée
        - Statistiques: {
            "total_iterations": int,
            "corrections_by_corrector": {corrector_name: count},
            "errors": [error_messages],
            "template_names_found": [list of template_names],
            "applicable_correctors_count": int
          }

    Examples:
        >>> from app.chains.correctors import CorrectorRegistry
        >>> registry = CorrectorRegistry()
        >>> # registry.register(MyCorrector())
        >>> structure = {"template_name": "layouts/container", "spacing": "invalid"}
        >>> corrected, stats = processSeriesOfCorrections(structure, registry)
        >>> print(stats["total_iterations"])
        1
    """
    logger = logging.getLogger(__name__)

    # Étape 1: Extraire les template_names
    template_names = extract_template_names(template_structure)
    logger.info(f"Template_names détectés: {template_names}")

    # Étape 2: Récupérer les correcteurs applicables
    applicable_correctors = registry.get_applicable_correctors(template_names)

    if not applicable_correctors:
        logger.info("Aucun correcteur applicable, structure inchangée")
        return template_structure, {
            "total_iterations": 0,
            "corrections_by_corrector": {},
            "errors": [],
            "template_names_found": list(template_names),
            "applicable_correctors_count": 0,
        }

    # Étape 3 & 4: Créer la queue et appliquer les corrections
    queue = CorrectionQueue(applicable_correctors, max_iterations)
    corrected_structure, stats = queue.process(template_structure)

    # Ajouter des infos supplémentaires aux stats
    stats["template_names_found"] = list(template_names)
    stats["applicable_correctors_count"] = len(applicable_correctors)

    # Log final
    logger.info(f"Corrections terminées: {stats}")

    return corrected_structure, stats
