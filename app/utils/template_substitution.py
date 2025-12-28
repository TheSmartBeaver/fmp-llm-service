from typing import Any, Dict, Union
import re
import copy
import logging

logger = logging.getLogger(__name__)


def substitute_template_values(template_structure: Any, source_data: Dict[str, Any], remove_unsubstituted: bool = False) -> Any:
    """
    Substitue les références {chemin} dans une structure de templates par les valeurs du JSON source.

    Gère les chemins simples, les tableaux avec [], et les objets avec ->.

    Exemples de chemins:
    - {course_title} : référence simple
    - {course_sections[]section_title} : parcourt un tableau
    - {course_sections[]tables[]infinitive} : tableaux imbriqués
    - {objet->champ} : navigation dans un objet

    Args:
        template_structure: La structure de templates avec des références {chemin}
        source_data: Le JSON source contenant les données
        remove_unsubstituted: Si True, supprime les champs contenant des références non substituées

    Returns:
        La structure avec toutes les références substituées par les valeurs réelles
    """
    try:
        logger.info("Starting template substitution")
        logger.debug(f"Template structure type: {type(template_structure)}")
        logger.debug(f"Source data keys: {list(source_data.keys()) if isinstance(source_data, dict) else 'N/A'}")

        # Set pour tracker les tableaux déjà en cours de traitement (évite les boucles infinies)
        processing_arrays = set()
        result = _process_template(template_structure, source_data, {}, processing_arrays)

        # Nettoyer les références non substituées si demandé
        if remove_unsubstituted:
            result = _remove_unsubstituted_references(result)

        logger.info("Template substitution completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during template substitution: {str(e)}", exc_info=True)
        raise


def _process_template(obj: Any, source_data: Dict[str, Any], context: Dict[str, Any], processing_arrays: set = None, depth: int = 0) -> Any:
    """
    Traite récursivement la structure en substituant les références.

    Args:
        obj: Objet à traiter
        source_data: Données source complètes
        context: Contexte des données courantes (pour les tableaux en cours de traitement)
        processing_arrays: Set des chemins de tableaux en cours de traitement
        depth: Profondeur de récursion (pour debugging)

    Returns:
        Objet traité
    """
    try:
        if processing_arrays is None:
            processing_arrays = set()

        # Protection contre la récursion excessive
        if depth > 50:
            logger.error(f"Maximum recursion depth exceeded at depth {depth}")
            raise RecursionError(f"Maximum recursion depth exceeded (depth={depth})")

        if isinstance(obj, str):
            return _substitute_string(obj, source_data, context)

        elif isinstance(obj, dict):
            # Vérifier si ce dict contient une référence de tableau qui nécessite un dépliage
            array_ref = _find_first_array_reference_in_dict(obj, context, processing_arrays)

            if array_ref:
                logger.debug(f"[Depth {depth}] Found array ref '{array_ref}', processing_arrays: {processing_arrays}, context keys: {list(context.keys())}")
                # Vérifier si ce tableau existe dans le contexte ou dans source_data
                array_data = _get_array_data(array_ref, source_data, context)

                # Si le tableau est déjà en cours de traitement, éviter la boucle infinie
                if array_ref in processing_arrays:
                    logger.warning(f"[Depth {depth}] Array '{array_ref}' is already being processed, skipping to avoid infinite loop")
                    result = {}
                    for key, value in obj.items():
                        result[key] = _process_template(value, source_data, context, processing_arrays, depth + 1)
                    return result
                # Si le tableau existe ET n'est pas vide, on doit déplier
                elif isinstance(array_data, list) and len(array_data) > 0:
                    logger.debug(f"[Depth {depth}] Found array reference: {array_ref}, will expand with {len(array_data)} items")
                    return _expand_dict_with_array(obj, source_data, context, array_ref, processing_arrays, depth)
                else:
                    # Le tableau n'existe pas ou est vide, traiter normalement (les références resteront)
                    logger.debug(f"[Depth {depth}] Array reference {array_ref} not found or empty, treating normally")
                    result = {}
                    for key, value in obj.items():
                        result[key] = _process_template(value, source_data, context, processing_arrays, depth + 1)
                    return result
            else:
                # Pas de tableau, traiter chaque champ normalement
                result = {}
                for key, value in obj.items():
                    result[key] = _process_template(value, source_data, context, processing_arrays, depth + 1)
                return result

        elif isinstance(obj, list):
            # Traiter chaque élément de la liste
            results = []
            for i, item in enumerate(obj):
                try:
                    processed = _process_template(item, source_data, context, processing_arrays, depth + 1)
                    # Si le traitement d'un item produit une liste, l'aplatir
                    if isinstance(processed, list) and _was_expanded_from_array(item):
                        results.extend(processed)
                    else:
                        results.append(processed)
                except Exception as e:
                    logger.error(f"[Depth {depth}] Error processing list item {i}: {str(e)}")
                    raise
            return results

        else:
            # Primitives (int, float, bool, None)
            return obj

    except RecursionError:
        raise
    except Exception as e:
        logger.error(f"[Depth {depth}] Error in _process_template: {str(e)}", exc_info=True)
        raise


def _substitute_string(text: str, source_data: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Substitue toutes les références {chemin} dans une string.

    Args:
        text: Texte avec des références
        source_data: Données source
        context: Contexte des tableaux en cours

    Returns:
        Texte avec les références substituées
    """
    pattern = r'\{([^}]+)\}'

    # Vérifier si le texte est EXACTEMENT une référence (ex: "{tips[]}" sans autre texte)
    if re.fullmatch(r'\{([^}]+)\}', text):
        # C'est une référence pure, on peut retourner la valeur telle quelle (y compris les listes)
        path = text[1:-1]  # Enlever les accolades
        value = _get_value_from_path(path, source_data, context)
        if value is not None:
            logger.debug(f"Resolved pure reference '{text}' to: {type(value)}")
            return value
        else:
            logger.debug(f"Could not resolve pure reference '{path}', keeping original")
            return text

    # Sinon, c'est du texte mixte avec des références, on doit substituer et retourner une string
    def replace_match(match):
        path = match.group(1)
        value = _get_value_from_path(path, source_data, context)

        if isinstance(value, str):
            return value
        elif value is not None:
            return str(value)
        else:
            logger.debug(f"Could not resolve reference '{path}', keeping original")
            return match.group(0)  # Garder la référence si pas trouvée

    result = re.sub(pattern, replace_match, text)
    if result != text:
        logger.debug(f"Substituted: '{text}' -> '{result}'")
    return result


def _get_value_from_path(path: str, source_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """
    Récupère une valeur depuis un chemin, en tenant compte du contexte.

    Args:
        path: Chemin (ex: "course_title", "course_sections[]section_id", "tables[]infinitive")
        source_data: Données source complètes
        context: Contexte des tableaux en cours de traitement

    Returns:
        La valeur trouvée
    """
    # Si le chemin contient [], extraire les parties pour résolution
    if '[]' in path:
        # Ex: "course_sections[]section_title", "tables[]infinitive", ou "course_sections[]tables[]infinitive"

        # Séparer les parties par []
        parts = path.split('[]')

        # Si on a exactement 2 parties (un seul tableau)
        if len(parts) == 2:
            array_name = parts[0]
            field_name = parts[1]

            # Si le champ est dans le contexte (on est déjà dans une itération du tableau)
            if field_name in context:
                return context[field_name]

            # Sinon, essayer avec -> si le field_name contient cela
            if '->' in field_name:
                value = _navigate_path(field_name, context)
                if value is not None:
                    return value

        # Si on a 3 parties ou plus (tableaux imbriqués comme "course_sections[]tables[]infinitive")
        elif len(parts) >= 3:
            # Ex: ["course_sections", "tables", "infinitive"]
            # On cherche le dernier champ dans le contexte (car on devrait être dans l'itération la plus profonde)
            final_field = parts[-1]

            # Si le dernier élément est vide, c'est un tableau de primitives (ex: "tips[]")
            if final_field == "":
                # Chercher le tableau dans le contexte
                # Ex: "course_sections[]tips[]" -> chercher "tips" dans le contexte
                array_name = parts[-2] if len(parts) >= 2 else None
                if array_name and array_name in context:
                    return context[array_name]
                return None

            if final_field in context:
                return context[final_field]

            # Sinon, essayer de résoudre le tableau intermédiaire + champ
            # Ex: si on a "course_sections[]tables[]infinitive" et qu'on est dans course_sections,
            # essayer "tables[]infinitive"
            for i in range(1, len(parts)):
                sub_path = '[]'.join(parts[i:])
                # Essayer de résoudre ce sous-chemin récursivement
                if '[]' in sub_path:
                    sub_parts = sub_path.split('[]')
                    if len(sub_parts) == 2 and sub_parts[1] in context:
                        return context[sub_parts[1]]

        # Pour les chemins qu'on ne peut pas résoudre, retourner None
        return None

    # Essayer d'abord dans le contexte (données courantes des tableaux)
    if '->' in path:
        # Navigation dans un objet
        value = _navigate_path(path, context)
        if value is not None:
            return value
        value = _navigate_path(path, source_data)
        return value
    else:
        # Chemin simple
        if path in context:
            return context[path]
        return source_data.get(path)


def _navigate_path(path: str, data: Dict[str, Any]) -> Any:
    """Navigate dans un chemin avec ->."""
    parts = path.split('->')
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _find_first_array_reference_in_dict(obj: dict, context: Dict[str, Any] = None, processing_arrays: set = None) -> Union[str, None]:
    """
    Trouve la première référence de tableau dans un dictionnaire qui n'est pas déjà en cours de traitement.

    Args:
        obj: Le dictionnaire à analyser
        context: Le contexte courant (pour résoudre les chemins imbriqués)
        processing_arrays: Set des tableaux déjà en cours de traitement

    Returns:
        Le chemin du tableau (ex: "course_sections", "tables") ou None
    """
    if context is None:
        context = {}
    if processing_arrays is None:
        processing_arrays = set()

    for value in obj.values():
        ref = _find_first_array_reference(value, processing_arrays)
        if ref:
            return ref
    return None


def _find_first_array_reference(obj: Any, processing_arrays: set = None) -> Union[str, None]:
    """
    Trouve la première référence de tableau dans un objet qui n'est pas déjà en cours de traitement.

    Args:
        obj: L'objet à analyser
        processing_arrays: Set des tableaux déjà en cours de traitement

    Returns:
        Le nom du tableau ou None
    """
    if processing_arrays is None:
        processing_arrays = set()

    if isinstance(obj, str):
        # Trouver TOUTES les références de tableau dans la chaîne
        matches = re.finditer(r'\{([^}]*\[\][^}]*)\}', obj)
        for match in matches:
            # Extraire le chemin du tableau complet
            full_ref = match.group(1)

            # Séparer tous les tableaux dans la référence
            # Ex: "course_sections[]tables[]conjugation_table[]pronoun_es" -> ["course_sections", "tables", "conjugation_table", "pronoun_es"]
            # Ex: "course_sections[]tips[]" -> ["course_sections", "tips", ""]
            parts = full_ref.split('[]')

            # Si la référence se termine par [] (dernière partie vide), on ne doit PAS déplier le dernier tableau
            # Ex: "{course_sections[]tips[]}" signifie "retourner le tableau tips complet", pas "déplier tips"
            # Donc on ignore la partie avant la dernière si la dernière est vide
            if parts[-1] == "" and len(parts) >= 3:
                # Ignorer le dernier tableau (celui avant la partie vide)
                parts_to_check = parts[:-2]
            else:
                # Cas normal: ignorer seulement la dernière partie (le champ final)
                parts_to_check = parts[:-1]

            # Parcourir les parties pour trouver le premier tableau qui n'est pas en cours de traitement
            for i, part in enumerate(parts_to_check):
                # Ignorer les parties vides
                if part and part not in processing_arrays:
                    return part

            # Si tous les tableaux sont déjà en cours de traitement, retourner None
            return None
        return None
    elif isinstance(obj, dict):
        for value in obj.values():
            ref = _find_first_array_reference(value, processing_arrays)
            if ref:
                return ref
    elif isinstance(obj, list):
        for item in obj:
            ref = _find_first_array_reference(item, processing_arrays)
            if ref:
                return ref
    return None


def _expand_dict_with_array(
    obj: dict,
    source_data: Dict[str, Any],
    context: Dict[str, Any],
    array_path: str,
    processing_arrays: set,
    depth: int = 0
) -> list:
    """
    Déplie un dictionnaire en créant une copie pour chaque élément du tableau.

    Args:
        obj: Le dictionnaire à déplier
        source_data: Données source
        context: Contexte courant
        array_path: Chemin du tableau (ex: "course_sections", "tables")
        processing_arrays: Set des tableaux en cours de traitement
        depth: Profondeur de récursion

    Returns:
        Liste de dictionnaires dépliés
    """
    try:
        # Marquer ce tableau comme en cours de traitement
        processing_arrays.add(array_path)
        logger.debug(f"[Depth {depth}] Added '{array_path}' to processing arrays: {processing_arrays}")

        # Récupérer le tableau
        array_data = _get_array_data(array_path, source_data, context)

        if not isinstance(array_data, list):
            logger.warning(f"[Depth {depth}] Array path '{array_path}' did not resolve to a list, got {type(array_data)}")
            processing_arrays.discard(array_path)
            return _process_template(obj, source_data, context, processing_arrays, depth)

        if len(array_data) == 0:
            logger.debug(f"[Depth {depth}] Array '{array_path}' is empty")
            processing_arrays.discard(array_path)
            return []

        logger.debug(f"[Depth {depth}] Expanding array '{array_path}' with {len(array_data)} items")

        # Créer une copie pour chaque élément du tableau
        results = []
        for i, array_item in enumerate(array_data):
            try:
                # Créer un nouveau contexte avec l'élément courant
                new_context = copy.copy(context)

                # Ajouter les champs de l'élément au contexte
                if isinstance(array_item, dict):
                    # Ajouter tous les champs (y compris les tableaux pour les traiter après)
                    new_context.update(array_item)

                    logger.debug(f"[Depth {depth}] Processing array item {i}/{len(array_data)}, context now has {len(new_context)} keys")
                else:
                    logger.debug(f"[Depth {depth}] Array item {i} is not a dict: {type(array_item)}")

                # Traiter la structure avec ce nouveau contexte
                # Copier le set pour que chaque branche ait son propre tracking
                new_processing = copy.copy(processing_arrays)
                result = _process_template(obj, source_data, new_context, new_processing, depth + 1)
                results.append(result)

            except Exception as e:
                logger.error(f"[Depth {depth}] Error processing array item {i} of '{array_path}': {str(e)}")
                raise

        logger.debug(f"[Depth {depth}] Successfully expanded array '{array_path}' into {len(results)} items")

        # Retirer le tableau des tableaux en cours de traitement
        processing_arrays.discard(array_path)
        return results

    except Exception as e:
        logger.error(f"[Depth {depth}] Error in _expand_dict_with_array for '{array_path}': {str(e)}", exc_info=True)
        processing_arrays.discard(array_path)
        raise


def _get_array_data(array_path: str, source_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """
    Récupère le tableau depuis le chemin.

    Essaie d'abord dans le contexte (pour les tableaux imbriqués),
    puis dans source_data.
    """
    try:
        # Essayer dans le contexte d'abord
        if array_path in context and isinstance(context[array_path], list):
            logger.debug(f"Found array '{array_path}' in context with {len(context[array_path])} items")
            return context[array_path]

        # Essayer dans source_data
        if '->' in array_path:
            result = _navigate_path(array_path, source_data)
            logger.debug(f"Navigated to '{array_path}' in source_data: {type(result)}")
            return result
        else:
            result = source_data.get(array_path)
            if result is not None:
                logger.debug(f"Found '{array_path}' in source_data: {type(result)}")
            elif array_path in context:
                # Le chemin existe dans context mais n'est pas une liste (c'est peut-être un champ simple)
                logger.debug(f"Array path '{array_path}' found in context but not as a list: {type(context.get(array_path))}")
            else:
                logger.debug(f"Array path '{array_path}' not found in context or source_data")
            return result

    except Exception as e:
        logger.error(f"Error getting array data for '{array_path}': {str(e)}", exc_info=True)
        raise


def _was_expanded_from_array(item: Any) -> bool:
    """
    Vérifie si un item contient une référence de tableau qui va être dépliée.
    """
    if isinstance(item, dict):
        return _find_first_array_reference_in_dict(item) is not None
    return False


def _remove_unsubstituted_references(obj: Any) -> Any:
    """
    Supprime récursivement les champs contenant des références non substituées.

    Args:
        obj: Objet à nettoyer

    Returns:
        Objet nettoyé sans références non substituées
    """
    if isinstance(obj, str):
        # Si c'est une string qui contient une référence non substituée, retourner None
        if re.search(r'\{[^}]+\}', obj):
            return None
        return obj

    elif isinstance(obj, dict):
        # Nettoyer chaque champ du dictionnaire
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = _remove_unsubstituted_references(value)
            # Ne garder que les valeurs qui ne sont pas None
            if cleaned_value is not None:
                cleaned[key] = cleaned_value
        return cleaned

    elif isinstance(obj, list):
        # Nettoyer chaque élément de la liste
        cleaned = []
        for item in obj:
            cleaned_item = _remove_unsubstituted_references(item)
            # Ne garder que les items qui ne sont pas None
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return cleaned

    else:
        # Primitives (int, float, bool, None)
        return obj
