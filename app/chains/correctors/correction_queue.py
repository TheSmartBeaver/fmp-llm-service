"""
Gestion de la file d'attente de corrections avec itérations multiples.
"""

from typing import Union, Dict, List, Any, Tuple
import json
import logging

from app.chains.correctors.base_corrector import BaseCorrector


class CorrectionQueue:
    """
    Gère la file d'attente de corrections avec multiples passes.

    Le système applique les correcteurs en boucle jusqu'à ce que:
    - Aucune correction ne soit appliquée (stabilité atteinte)
    - Le nombre maximum d'itérations soit atteint
    """

    def __init__(self, correctors: List[BaseCorrector], max_iterations: int = 10):
        """
        Args:
            correctors: Liste des correcteurs à appliquer
            max_iterations: Nombre maximum d'itérations (défaut: 10)
        """
        self.correctors = correctors
        self.max_iterations = max_iterations
        self.logger = logging.getLogger(__name__)

    def process(
        self, json_obj: Union[Dict, List]
    ) -> Tuple[Union[Dict, List], Dict[str, Any]]:
        """
        Applique les correcteurs en boucle jusqu'à stabilisation.

        Chaque itération:
        1. Sérialise le JSON en string
        2. Pour chaque correcteur:
           a. Détecte si une erreur est présente (via regex)
           b. Si oui, applique la correction
        3. Si aucune correction n'a été appliquée, arrête
        4. Sinon, continue avec l'itération suivante

        Args:
            json_obj: Structure JSON à corriger

        Returns:
            Tuple contenant:
            - Structure JSON corrigée
            - Statistiques: {
                "total_iterations": int,
                "corrections_by_corrector": {corrector_name: count},
                "errors": [error_messages]
              }
        """
        stats = {
            "total_iterations": 0,
            "corrections_by_corrector": {},
            "errors": [],
        }

        for iteration in range(self.max_iterations):
            stats["total_iterations"] = iteration + 1
            json_str = json.dumps(json_obj, ensure_ascii=False)

            corrections_applied = False

            # Chaque correcteur vérifie s'il doit intervenir
            for corrector in self.correctors:
                corrector_name = corrector.name

                try:
                    if corrector.detect_error(json_str):
                        self.logger.info(
                            f"[Iteration {iteration + 1}] {corrector_name}: "
                            f"Erreur détectée, application de la correction"
                        )

                        # Appliquer la correction
                        json_obj = corrector.apply_correction(json_obj)

                        # Mettre à jour les stats
                        if corrector_name not in stats["corrections_by_corrector"]:
                            stats["corrections_by_corrector"][corrector_name] = 0
                        stats["corrections_by_corrector"][corrector_name] += 1

                        corrections_applied = True

                        # Re-sérialiser pour les prochains correcteurs de cette itération
                        json_str = json.dumps(json_obj, ensure_ascii=False)

                except Exception as e:
                    error_msg = f"{corrector_name}: Échec - {str(e)}"
                    self.logger.error(error_msg)
                    stats["errors"].append(error_msg)
                    # Continuer avec les autres correcteurs

            # Si aucune correction n'a été appliquée, on a atteint la stabilité
            if not corrections_applied:
                self.logger.info(f"Stabilité atteinte après {iteration + 1} itération(s)")
                break
        else:
            # Max iterations atteint
            self.logger.warning(
                f"Limite de {self.max_iterations} itérations atteinte"
            )

        return json_obj, stats
