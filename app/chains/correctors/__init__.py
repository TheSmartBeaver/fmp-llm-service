"""
Module de correction de structures JSON de templates.

Ce module contient le système de correcteurs permettant de détecter
et corriger automatiquement des erreurs dans les structures JSON générées.
"""

from app.chains.correctors.base_corrector import BaseCorrector
from app.chains.correctors.corrector_registry import CorrectorRegistry
from app.chains.correctors.correction_queue import CorrectionQueue
from app.chains.correctors.utils import extract_template_names, processSeriesOfCorrections

__all__ = [
    "BaseCorrector",
    "CorrectorRegistry",
    "CorrectionQueue",
    "extract_template_names",
    "processSeriesOfCorrections",
]
