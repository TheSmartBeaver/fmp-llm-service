"""
Correcteur pour supprimer les blocs JSON dupliqués.
"""

from typing import Any, Set
import re
import json

from app.chains.correctors.base_corrector import BaseCorrector


class DuplicateBlockRemoverCorrector(BaseCorrector):
    """
    Détecte et supprime les blocs JSON dupliqués dans toute la structure.

    Garde la première occurrence de chaque bloc unique et supprime les suivantes.

    Comparaison stricte : tous les champs doivent être identiques pour considérer
    deux blocs comme dupliqués.

    Portée : Toute la structure globale (pas seulement au sein d'une même liste).

    Templates concernés: Tous les templates susceptibles d'être dupliqués
    (principalement les blocs de contenu statique)

    Mode d'applicabilité: "any" (au moins un template doit être présent)
    """

    template_names = [
        "text/sous_titre",
        "text/title",
        "text/description",
        "text/paragraph",
        "layouts/vertical_column/container",
        "layouts/horizontal_line/container",
        "temporal/timeline_vertical/container",
    ]

    # Pattern simple : détecte la présence de blocs avec template_name
    # La vraie logique de détection des doublons est dans apply_correction
    error_pattern = re.compile(r'"template_name"\s*:\s*"[^"]+"')

    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "DuplicateBlockRemoverCorrector"

    def detect_error(self, json_str: str) -> bool:
        """
        Détecte si le JSON contient des doublons.

        Surcharge de la méthode de base pour vérifier réellement
        la présence de doublons au lieu d'utiliser simplement une regex.

        Args:
            json_str: JSON sérialisé en string

        Returns:
            True si des doublons sont détectés, False sinon
        """
        import json as json_module

        try:
            json_obj = json_module.loads(json_str)
            seen_signatures: Set[str] = set()
            has_duplicates = False

            def check_duplicates(obj: Any) -> None:
                """Fonction récursive pour détecter les doublons."""
                nonlocal has_duplicates

                if isinstance(obj, dict):
                    # Si c'est un bloc avec template_name, vérifier s'il est dupliqué
                    if "template_name" in obj:
                        signature = self._calculate_signature(obj)
                        if signature in seen_signatures:
                            has_duplicates = True
                            return
                        seen_signatures.add(signature)

                    # Parcourir récursivement les valeurs
                    for value in obj.values():
                        check_duplicates(value)
                        if has_duplicates:
                            return

                elif isinstance(obj, list):
                    for item in obj:
                        check_duplicates(item)
                        if has_duplicates:
                            return

            check_duplicates(json_obj)
            return has_duplicates

        except Exception:
            # En cas d'erreur de parsing, utiliser la regex par défaut
            return super().detect_error(json_str)

    def apply_correction(self, json_obj: Any) -> Any:
        """
        Supprime les blocs dupliqués de toute la structure.

        Algorithme:
        1. Parcourir la structure et collecter les signatures des blocs déjà vus
        2. Pour chaque bloc avec template_name, calculer sa signature
        3. Garder le premier de chaque signature, supprimer les suivants
        4. Filtrer les None lors du parcours récursif

        Args:
            json_obj: Structure JSON à corriger

        Returns:
            Structure JSON sans doublons
        """
        # Set pour stocker les signatures des blocs déjà rencontrés
        seen_signatures: Set[str] = set()

        def remove_duplicates(obj: Any) -> Any:
            """Fonction récursive qui supprime les doublons."""

            if isinstance(obj, dict):
                # Si c'est un bloc avec template_name, vérifier s'il est dupliqué
                if "template_name" in obj:
                    signature = self._calculate_signature(obj)

                    # Si on a déjà vu ce bloc exact, le marquer pour suppression
                    if signature in seen_signatures:
                        return None  # Marquer pour suppression

                    # Sinon, ajouter la signature aux blocs vus
                    seen_signatures.add(signature)

                # Parcourir récursivement toutes les valeurs du dict
                result = {}
                for key, value in obj.items():
                    corrected_value = remove_duplicates(value)
                    # Ne pas inclure les valeurs None (doublons supprimés)
                    # SAUF si c'est une valeur None légitime (template_name: null)
                    if corrected_value is not None or value is None:
                        result[key] = corrected_value

                return result

            elif isinstance(obj, list):
                # Filtrer les None (doublons supprimés) dans les listes
                result = []
                for item in obj:
                    corrected_item = remove_duplicates(item)
                    # Ne garder que les items non-None
                    if corrected_item is not None:
                        result.append(corrected_item)
                return result

            # Pour les autres types (str, int, bool, None), retourner tel quel
            return obj

        return remove_duplicates(json_obj)

    def _calculate_signature(self, block: dict) -> str:
        """
        Calcule une signature unique pour un bloc JSON.

        Utilise JSON canonique (clés triées) pour garantir que deux blocs
        avec le même contenu (mais potentiellement dans un ordre différent)
        ont la même signature.

        Args:
            block: Bloc JSON (dict) à signer

        Returns:
            Signature du bloc (string JSON canonique)
        """
        return json.dumps(block, sort_keys=True, ensure_ascii=False)
