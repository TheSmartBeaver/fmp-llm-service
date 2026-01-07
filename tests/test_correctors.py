"""
Tests pour le système de correcteurs.
"""

import pytest
from app.chains.correctors import (
    CorrectorRegistry,
    processSeriesOfCorrections,
    extract_template_names,
)
from app.chains.correctors.implementations import LayoutSpacingCorrector


def test_extract_template_names():
    """Test de l'extraction des template_names."""
    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "1rem",
        "items": [
            {
                "template_name": "text/title",
                "text": "Hello",
            },
            {
                "template_name": "text/description",
                "text": "World",
            },
        ],
    }

    template_names = extract_template_names(structure)

    assert len(template_names) == 3
    assert "layouts/vertical_column/container" in template_names
    assert "text/title" in template_names
    assert "text/description" in template_names


def test_layout_spacing_corrector_detection():
    """Test de la détection d'erreur par LayoutSpacingCorrector."""
    corrector = LayoutSpacingCorrector()

    # JSON avec erreur (spacing invalide)
    json_with_error = '{"template_name": "layouts/vertical_column/container", "spacing": "invalid"}'
    assert corrector.detect_error(json_with_error) is True

    # JSON sans erreur (spacing valide)
    json_without_error = '{"template_name": "layouts/vertical_column/container", "spacing": "1rem"}'
    assert corrector.detect_error(json_without_error) is False


def test_layout_spacing_corrector_correction():
    """Test de la correction par LayoutSpacingCorrector."""
    corrector = LayoutSpacingCorrector()

    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "invalid_value",
        "items": [
            {
                "template_name": "layouts/horizontal_line/container",
                "spacing": "xyz123",
            }
        ],
    }

    corrected = corrector.apply_correction(structure)

    assert corrected["spacing"] == "1rem"
    assert corrected["items"][0]["spacing"] == "1rem"


def test_corrector_registry():
    """Test du registre de correcteurs."""
    registry = CorrectorRegistry()

    # Enregistrer un correcteur
    corrector = LayoutSpacingCorrector()
    registry.register(corrector)

    assert registry.count() == 1

    # Test de sélection des correcteurs applicables
    template_names = {"layouts/vertical_column/container", "text/title"}
    applicable = registry.get_applicable_correctors(template_names)

    # LayoutSpacingCorrector devrait être applicable car "layouts/vertical_column/container" est présent
    assert len(applicable) == 1
    assert applicable[0].name == "LayoutSpacingCorrector"

    # Test sans template_names correspondants
    template_names_no_match = {"text/title", "text/description"}
    applicable_no_match = registry.get_applicable_correctors(template_names_no_match)

    # Aucun correcteur applicable
    assert len(applicable_no_match) == 0


def test_process_series_of_corrections():
    """Test du processus complet de corrections."""
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "invalid",
        "items": [
            {
                "template_name": "text/title",
                "text": "Test",
            }
        ],
    }

    corrected, stats = processSeriesOfCorrections(structure, registry)

    # Vérifier la correction
    assert corrected["spacing"] == "1rem"

    # Vérifier les stats
    assert stats["total_iterations"] >= 1
    assert "LayoutSpacingCorrector" in stats["corrections_by_corrector"]
    assert stats["corrections_by_corrector"]["LayoutSpacingCorrector"] >= 1
    assert len(stats["errors"]) == 0
    assert "layouts/vertical_column/container" in stats["template_names_found"]
    assert stats["applicable_correctors_count"] == 1


def test_process_no_applicable_correctors():
    """Test quand aucun correcteur n'est applicable."""
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

    # Structure sans template_names concernés par LayoutSpacingCorrector
    structure = {
        "template_name": "text/title",
        "text": "Test",
    }

    corrected, stats = processSeriesOfCorrections(structure, registry)

    # Structure inchangée
    assert corrected == structure

    # Stats indiquant aucune correction
    assert stats["total_iterations"] == 0
    assert len(stats["corrections_by_corrector"]) == 0
    assert stats["applicable_correctors_count"] == 0


def test_multiple_iterations():
    """Test des itérations multiples."""
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

    # Structure avec erreurs imbriquées
    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "bad",
        "items": [
            {
                "template_name": "layouts/vertical_column/container",
                "spacing": "also_bad",
                "items": [
                    {
                        "template_name": "layouts/horizontal_line/container",
                        "spacing": "still_bad",
                    }
                ],
            }
        ],
    }

    corrected, stats = processSeriesOfCorrections(structure, registry)

    # Toutes les erreurs doivent être corrigées
    assert corrected["spacing"] == "1rem"
    assert corrected["items"][0]["spacing"] == "1rem"
    assert corrected["items"][0]["items"][0]["spacing"] == "1rem"

    # Une seule itération devrait suffire car tout est corrigé en une passe
    assert stats["total_iterations"] == 1
    assert stats["corrections_by_corrector"]["LayoutSpacingCorrector"] == 1


def test_list_structure():
    """Test avec une structure qui est une liste à la racine."""
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

    structure = [
        {
            "template_name": "layouts/vertical_column/container",
            "spacing": "invalid",
        },
        {
            "template_name": "text/title",
            "text": "Test",
        },
    ]

    corrected, stats = processSeriesOfCorrections(structure, registry)

    # Vérifier la correction
    assert corrected[0]["spacing"] == "1rem"
    assert corrected[1]["text"] == "Test"

    # Vérifier les stats
    assert stats["total_iterations"] >= 1
    assert stats["corrections_by_corrector"]["LayoutSpacingCorrector"] >= 1
