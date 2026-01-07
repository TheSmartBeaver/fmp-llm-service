"""
Classe de base abstraite pour les correcteurs de JSON.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Set, Literal
import re


class BaseCorrector(ABC):
    """
    Correcteur de base pour détecter et corriger des patterns JSON.

    Chaque correcteur concret doit:
    1. Définir les template_names concernés
    2. Définir un error_pattern (regex) pour détecter l'erreur
    3. Définir applicability_mode ("any" ou "all")
    4. Implémenter name pour identifier le correcteur
    5. Implémenter apply_correction pour corriger le JSON
    """

    # Templates concernés par ce correcteur
    # Exemple: ["layouts/vertical_column/container", "layouts/horizontal_line/container"]
    template_names: List[str] = []

    # Pattern regex pour détecter l'erreur
    # Exemple: re.compile(r'"spacing"\s*:\s*"[^0-9]')
    error_pattern: re.Pattern

    # Mode d'applicabilité du correcteur
    # - "any": Le correcteur est applicable si AU MOINS UN de ses template_names est présent
    # - "all": Le correcteur est applicable si TOUS ses template_names sont présents
    applicability_mode: Literal["any", "all"] = "any"

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nom du correcteur pour le logging.

        Returns:
            Nom identifiant unique du correcteur
        """
        pass

    def is_applicable(self, template_names_present: Set[str]) -> bool:
        """
        Détermine si le correcteur est applicable en fonction des template_names présents.

        La logique dépend de l'attribut applicability_mode:
        - "any": Au moins UN template_name du correcteur doit être présent
        - "all": TOUS les template_names du correcteur doivent être présents

        Args:
            template_names_present: Ensemble des template_names présents dans la structure

        Returns:
            True si le correcteur est applicable, False sinon

        Examples:
            >>> # Correcteur avec mode "any"
            >>> corrector.template_names = ["layouts/container", "text/title"]
            >>> corrector.applicability_mode = "any"
            >>> corrector.is_applicable({"layouts/container", "other/template"})
            True  # Au moins un template_name correspond

            >>> # Correcteur avec mode "all"
            >>> corrector.applicability_mode = "all"
            >>> corrector.is_applicable({"layouts/container"})
            False  # Tous les template_names ne sont pas présents
            >>> corrector.is_applicable({"layouts/container", "text/title"})
            True  # Tous les template_names sont présents
        """
        if not self.template_names:
            # Si aucun template_name n'est défini, le correcteur n'est jamais applicable
            return False

        corrector_templates = set(self.template_names)

        if self.applicability_mode == "all":
            # Mode "all": TOUS les template_names du correcteur doivent être présents
            return corrector_templates.issubset(template_names_present)
        else:
            # Mode "any" (par défaut): AU MOINS UN template_name doit être présent
            return bool(corrector_templates.intersection(template_names_present))

    def detect_error(self, json_str: str) -> bool:
        """
        Détecte si le JSON contient l'erreur via regex.

        Args:
            json_str: JSON sérialisé en string

        Returns:
            True si l'erreur est détectée, False sinon
        """
        return bool(self.error_pattern.search(json_str))

    @abstractmethod
    def apply_correction(self, json_obj: Any) -> Any:
        """
        Applique la correction au JSON.

        Cette méthode doit parcourir récursivement la structure JSON
        et appliquer les corrections nécessaires.

        Args:
            json_obj: Structure JSON (dict, list ou autre type)

        Returns:
            Structure JSON corrigée
        """
        pass
