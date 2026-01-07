"""
Correcteur pour remonter text/liste_exemples hors des containers inappropriés.
"""

from typing import Any, Optional
import re

from app.chains.correctors.base_corrector import BaseCorrector


class ListeExemplesHoistCorrector(BaseCorrector):
    """
    Remonte text/liste_exemples hors des containers inappropriés.

    Détecte les cas où text/liste_exemples est imbriqué dans des containers
    dont le template_name ne commence pas par "layouts/", et remonte le
    text/liste_exemples au niveau le plus haut possible sans perte d'information.

    Critère d'arrêt: On remonte jusqu'à atteindre un niveau où, après suppression
    du champ contenant l'imbrication, il reste d'autres propriétés que template_name.

    Templates concernés: text/liste_exemples

    Mode d'applicabilité: "any"
    """

    template_names = [
        "text/liste_exemples",
    ]

    # Pattern simple pour détecter la présence de text/liste_exemples
    # La vraie logique de détection est dans detect_error()
    error_pattern = re.compile(r'"template_name"\s*:\s*"text/liste_exemples"')

    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "ListeExemplesHoistCorrector"

    def detect_error(self, json_str: str) -> bool:
        """
        Détecte si text/liste_exemples peut être remonté.

        La détection est cohérente avec la correction : un text/liste_exemples
        est inapproprié seulement s'il peut être remonté selon les mêmes critères
        que apply_correction.

        Args:
            json_str: JSON sérialisé en string

        Returns:
            True si text/liste_exemples peut être remonté, False sinon
        """
        import json as json_module

        try:
            json_obj = json_module.loads(json_str)
            return self._can_hoist_anywhere(json_obj, is_root=True)
        except Exception:
            # En cas d'erreur de parsing, utiliser la regex par défaut
            return super().detect_error(json_str)

    def _can_hoist_anywhere(self, obj: Any, is_root: bool = False) -> bool:
        """
        Vérifie si un text/liste_exemples peut être remonté quelque part dans la structure.

        Utilise la même logique que _hoist_liste_exemples pour déterminer
        si une remontée est possible.

        Args:
            obj: Objet à vérifier
            is_root: True si c'est l'objet racine

        Returns:
            True si une remontée est possible quelque part
        """
        if isinstance(obj, dict):
            # Vérifier pour chaque propriété
            for key, value in obj.items():
                # Chercher si cette valeur contient un text/liste_exemples
                liste_exemples = self._find_liste_exemples(value)

                if liste_exemples is not None:
                    # On a trouvé un text/liste_exemples dans cette branche
                    # Vérifier si on peut le remonter selon les mêmes critères que apply_correction
                    other_props_count = self._count_other_properties(obj, exclude_key=key)
                    has_version_here = "version" in obj
                    has_version_in_path = self._contains_version(value)

                    # Si on peut remonter à ce niveau, c'est qu'il y a une correction à faire
                    if not is_root and other_props_count == 0 and not has_version_here and not has_version_in_path:
                        return True

                    # Sinon, vérifier récursivement dans cette branche
                    if self._can_hoist_anywhere(value, is_root=False):
                        return True
                else:
                    # Pas de liste_exemples dans cette branche, vérifier récursivement
                    if self._can_hoist_anywhere(value, is_root=False):
                        return True

        elif isinstance(obj, list):
            for item in obj:
                if self._can_hoist_anywhere(item, is_root=False):
                    return True

        return False

    def apply_correction(self, json_obj: Any) -> Any:
        """
        Remonte text/liste_exemples au niveau le plus haut possible sans perte d'information.

        Algorithme:
        1. Parcourir récursivement la structure
        2. Détecter les text/liste_exemples
        3. Les remonter jusqu'à atteindre un niveau où il y a d'autres propriétés à préserver

        Args:
            json_obj: Structure JSON à corriger

        Returns:
            Structure JSON corrigée
        """
        return self._hoist_liste_exemples(json_obj, is_root=True)

    def _hoist_liste_exemples(self, obj: Any, is_root: bool = False) -> Any:
        """
        Fonction récursive pour remonter text/liste_exemples.

        Args:
            obj: Objet à traiter
            is_root: True si c'est l'objet racine (ne jamais le remplacer complètement)

        Returns:
            Objet traité (potentiellement remplacé par text/liste_exemples)
        """
        if isinstance(obj, dict):
            # Si c'est text/liste_exemples, le retourner tel quel
            if obj.get("template_name") == "text/liste_exemples":
                return obj

            # Traiter récursivement toutes les propriétés SAUF si on peut
            # remplacer directement l'objet actuel
            for key, value in list(obj.items()):
                # Chercher si cette valeur contient un text/liste_exemples
                liste_exemples = self._find_liste_exemples(value)

                if liste_exemples is not None:
                    # On a trouvé un text/liste_exemples dans cette branche
                    # Vérifier si on peut remplacer l'objet actuel par text/liste_exemples
                    other_props_count = self._count_other_properties(obj, exclude_key=key)
                    has_version_here = "version" in obj
                    has_version_in_path = self._contains_version(value)

                    # Ne JAMAIS remplacer la racine complètement
                    # Ne JAMAIS traverser un niveau avec "version"
                    if not is_root and other_props_count == 0 and not has_version_here and not has_version_in_path:
                        # Aucune autre propriété importante ET pas de version ici ou dans le chemin ET pas la racine
                        # → On peut remplacer tout l'objet par text/liste_exemples
                        return liste_exemples
                    else:
                        # Il y a d'autres propriétés importantes OU il y a "version" quelque part OU c'est la racine
                        # → On s'arrête ici et on traite récursivement cette valeur
                        obj[key] = self._hoist_liste_exemples(value, is_root=False)
                        # Ne pas traiter les autres clés, on a fini
                        return obj
                else:
                    # Pas de liste_exemples dans cette branche, traiter normalement
                    obj[key] = self._hoist_liste_exemples(value, is_root=False)

            return obj

        elif isinstance(obj, list):
            return [self._hoist_liste_exemples(item, is_root=False) for item in obj]

        return obj

    def _contains_version(self, obj: Any) -> bool:
        """
        Vérifie si un objet ou ses enfants contiennent le champ "version".

        Args:
            obj: Objet à vérifier

        Returns:
            True si "version" est présent quelque part dans l'arbre
        """
        if isinstance(obj, dict):
            if "version" in obj:
                return True
            for value in obj.values():
                if self._contains_version(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._contains_version(item):
                    return True
        return False

    def _find_liste_exemples(self, obj: Any) -> Optional[dict]:
        """
        Cherche récursivement un text/liste_exemples dans un objet.

        Args:
            obj: Objet dans lequel chercher

        Returns:
            Le premier text/liste_exemples trouvé, ou None
        """
        if isinstance(obj, dict):
            if obj.get("template_name") == "text/liste_exemples":
                return obj

            # Chercher dans toutes les valeurs
            for value in obj.values():
                result = self._find_liste_exemples(value)
                if result is not None:
                    return result

        elif isinstance(obj, list):
            for item in obj:
                result = self._find_liste_exemples(item)
                if result is not None:
                    return result

        return None

    def _count_other_properties(self, obj: dict, exclude_key: str) -> int:
        """
        Compte les propriétés "importantes" d'un dict.

        Exclut:
        - exclude_key (le champ contenant l'imbrication qu'on veut supprimer)
        - "template_name" (toujours présent, pas une info à préserver)

        Args:
            obj: Dict dont on compte les propriétés
            exclude_key: Clé à exclure du comptage

        Returns:
            Nombre de propriétés importantes restantes
        """
        properties = set(obj.keys())
        properties.discard(exclude_key)  # Retirer le champ d'imbrication
        properties.discard("template_name")  # Retirer template_name
        return len(properties)
