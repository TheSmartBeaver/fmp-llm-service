"""
Correcteur pour les valeurs de spacing invalides dans les layouts.
"""

from typing import Any
import re

from app.chains.correctors.base_corrector import BaseCorrector


class LayoutSpacingCorrector(BaseCorrector):
    """
    Corrige les valeurs de spacing invalides dans les layouts.

    Détecte les cas où "spacing" contient une valeur qui ne commence pas
    par un chiffre (ex: "spacing": "invalid") et les remplace par "1rem".

    Templates concernés:
    - layouts/vertical_column/container
    - layouts/horizontal_line/container

    Mode d'applicabilité: "any" (au moins un des templates doit être présent)
    """

    template_names = [
        "layouts/vertical_column/container",
        "layouts/horizontal_line/container",
    ]

    # Détecte spacing avec valeur non-numérique au début
    # Ex: "spacing": "invalid" ou "spacing": "abc123"
    error_pattern = re.compile(r'"spacing"\s*:\s*"[^0-9]')

    # Mode d'applicabilité : le correcteur s'active si AU MOINS UN template est présent
    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "LayoutSpacingCorrector"

    def apply_correction(self, json_obj: Any) -> Any:
        """
        Remplace les spacing invalides par '1rem'.

        Parcourt récursivement la structure et corrige tous les
        objets ayant un template_name concerné et un spacing invalide.

        Args:
            json_obj: Structure JSON à corriger

        Returns:
            Structure JSON corrigée
        """
        if isinstance(json_obj, dict):
            # Vérifier si ce dict est un template concerné
            if json_obj.get("template_name") in self.template_names:
                if "spacing" in json_obj:
                    spacing = json_obj["spacing"]
                    # Si c'est une string qui ne commence pas par un chiffre
                    if isinstance(spacing, str) and spacing and not spacing[0].isdigit():
                        json_obj["spacing"] = "1rem"

            # Récursion sur toutes les valeurs du dict
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)

        elif isinstance(json_obj, list):
            # Récursion sur tous les items de la liste
            return [self.apply_correction(item) for item in json_obj]

        return json_obj
