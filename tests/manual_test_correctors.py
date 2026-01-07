"""
Test manuel du système de correcteurs.
"""

from app.chains.correctors import (
    CorrectorRegistry,
    processSeriesOfCorrections,
    extract_template_names,
)
from app.chains.correctors.implementations import LayoutSpacingCorrector


def test_extract_template_names():
    print("\n=== Test: extract_template_names ===")
    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "1rem",
        "items": [
            {"template_name": "text/title", "text": "Hello"},
            {"template_name": "text/description", "text": "World"},
        ],
    }

    template_names = extract_template_names(structure)
    print(f"Template names trouvés: {template_names}")
    assert len(template_names) == 3
    assert "layouts/vertical_column/container" in template_names
    assert "text/title" in template_names
    assert "text/description" in template_names
    print("✅ PASS")


def test_layout_spacing_corrector_detection():
    print("\n=== Test: LayoutSpacingCorrector detection ===")
    corrector = LayoutSpacingCorrector()

    # JSON avec erreur
    json_with_error = '{"template_name": "layouts/vertical_column/container", "spacing": "invalid"}'
    result = corrector.detect_error(json_with_error)
    print(f"Détection erreur (attendu True): {result}")
    assert result is True

    # JSON sans erreur
    json_without_error = '{"template_name": "layouts/vertical_column/container", "spacing": "1rem"}'
    result = corrector.detect_error(json_without_error)
    print(f"Détection sans erreur (attendu False): {result}")
    assert result is False
    print("✅ PASS")


def test_layout_spacing_corrector_correction():
    print("\n=== Test: LayoutSpacingCorrector correction ===")
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

    print(f"Structure avant: {structure}")
    corrected = corrector.apply_correction(structure)
    print(f"Structure après: {corrected}")

    assert corrected["spacing"] == "1rem"
    assert corrected["items"][0]["spacing"] == "1rem"
    print("✅ PASS")


def test_corrector_registry():
    print("\n=== Test: CorrectorRegistry ===")
    registry = CorrectorRegistry()
    corrector = LayoutSpacingCorrector()
    registry.register(corrector)

    print(f"Nombre de correcteurs: {registry.count()}")
    assert registry.count() == 1

    template_names = {"layouts/vertical_column/container", "text/title"}
    applicable = registry.get_applicable_correctors(template_names)
    print(f"Correcteurs applicables: {[c.name for c in applicable]}")
    assert len(applicable) == 1
    assert applicable[0].name == "LayoutSpacingCorrector"

    template_names_no_match = {"text/title", "text/description"}
    applicable_no_match = registry.get_applicable_correctors(template_names_no_match)
    print(f"Correcteurs applicables (sans match): {len(applicable_no_match)}")
    assert len(applicable_no_match) == 0
    print("✅ PASS")


def test_process_series_of_corrections():
    print("\n=== Test: processSeriesOfCorrections ===")
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

    structure = {
        "template_name": "layouts/vertical_column/container",
        "spacing": "invalid",
        "items": [{"template_name": "text/title", "text": "Test"}],
    }

    print(f"Structure avant: {structure}")
    corrected, stats = processSeriesOfCorrections(structure, registry)
    print(f"Structure après: {corrected}")
    print(f"Stats: {stats}")

    assert corrected["spacing"] == "1rem"
    assert stats["total_iterations"] >= 1
    assert "LayoutSpacingCorrector" in stats["corrections_by_corrector"]
    assert len(stats["errors"]) == 0
    print("✅ PASS")


def test_multiple_nested_corrections():
    print("\n=== Test: Corrections imbriquées multiples ===")
    registry = CorrectorRegistry()
    registry.register(LayoutSpacingCorrector())

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

    print(f"Structure avant (3 erreurs imbriquées)")
    corrected, stats = processSeriesOfCorrections(structure, registry)
    print(f"Structure après: spacing racine={corrected['spacing']}, "
          f"niveau 1={corrected['items'][0]['spacing']}, "
          f"niveau 2={corrected['items'][0]['items'][0]['spacing']}")
    print(f"Stats: {stats}")

    assert corrected["spacing"] == "1rem"
    assert corrected["items"][0]["spacing"] == "1rem"
    assert corrected["items"][0]["items"][0]["spacing"] == "1rem"
    print("✅ PASS")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTS DU SYSTÈME DE CORRECTEURS")
    print("=" * 60)

    try:
        test_extract_template_names()
        test_layout_spacing_corrector_detection()
        test_layout_spacing_corrector_correction()
        test_corrector_registry()
        test_process_series_of_corrections()
        test_multiple_nested_corrections()

        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("=" * 60 + "\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
