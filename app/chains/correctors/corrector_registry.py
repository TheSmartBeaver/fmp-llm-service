"""
Registre centralisé de tous les correcteurs.
"""

from typing import List, Set
import logging

from app.chains.correctors.base_corrector import BaseCorrector


class CorrectorRegistry:
    """
    Registre centralisé de tous les correcteurs.

    Le registre permet de:
    1. Enregistrer des correcteurs
    2. Récupérer uniquement les correcteurs applicables selon les template_names présents
    """

    def __init__(self):
        """Initialise un registre vide."""
        self._correctors: List[BaseCorrector] = []
        self.logger = logging.getLogger(__name__)

    def register(self, corrector: BaseCorrector) -> None:
        """
        Enregistre un correcteur dans le registre.

        Args:
            corrector: Instance de correcteur à enregistrer
        """
        self._correctors.append(corrector)
        self.logger.debug(f"Correcteur enregistré: {corrector.name}")

    def get_applicable_correctors(
        self, template_names: Set[str]
    ) -> List[BaseCorrector]:
        """
        Retourne les correcteurs applicables selon les template_names présents.

        Chaque correcteur détermine lui-même s'il est applicable via sa méthode
        is_applicable(), qui utilise son applicability_mode ("any" ou "all").

        Args:
            template_names: Ensemble des template_names présents dans la structure

        Returns:
            Liste des correcteurs applicables
        """
        applicable = []

        for corrector in self._correctors:
            # Utiliser la méthode is_applicable() du correcteur
            if corrector.is_applicable(template_names):
                applicable.append(corrector)
                self.logger.debug(
                    f"Correcteur {corrector.name} est applicable "
                    f"(mode: {corrector.applicability_mode}, "
                    f"templates: {corrector.template_names})"
                )

        self.logger.info(
            f"{len(applicable)}/{len(self._correctors)} correcteurs applicables"
        )

        return applicable

    def get_all_correctors(self) -> List[BaseCorrector]:
        """
        Retourne tous les correcteurs enregistrés.

        Returns:
            Liste de tous les correcteurs
        """
        return self._correctors.copy()

    def count(self) -> int:
        """
        Retourne le nombre de correcteurs enregistrés.

        Returns:
            Nombre de correcteurs
        """
        return len(self._correctors)
