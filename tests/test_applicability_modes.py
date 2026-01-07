"""
Tests pour les modes d'applicabilité des correcteurs (any vs all).
"""

from typing import Any
import re
from app.chains.correctors.base_corrector import BaseCorrector
from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections


# Correcteur avec mode "any" (par défaut)
class AnyModeCorrector(BaseCorrector):
    """Correcteur avec mode 'any'."""

    template_names = ["template/a", "template/b", "template/c"]
    error_pattern = re.compile(r'"field_a"\s*:\s*"bad"')
    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "AnyModeCorrector"

    def apply_correction(self, json_obj: Any) -> Any:
        if isinstance(json_obj, dict):
            if "field_a" in json_obj and json_obj["field_a"] == "bad":
                json_obj["field_a"] = "good_any"
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)
        elif isinstance(json_obj, list):
            return [self.apply_correction(item) for item in json_obj]
        return json_obj


# Correcteur avec mode "all"
class AllModeCorrector(BaseCorrector):
    """Correcteur avec mode 'all'."""

    template_names = ["template/x", "template/y"]
    error_pattern = re.compile(r'"field_all"\s*:\s*"bad"')
    applicability_mode = "all"

    @property
    def name(self) -> str:
        return "AllModeCorrector"

    def apply_correction(self, json_obj: Any) -> Any:
        if isinstance(json_obj, dict):
            if "field_all" in json_obj and json_obj["field_all"] == "bad":
                json_obj["field_all"] = "good_all"
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)
        elif isinstance(json_obj, list):
            return [self.apply_correction(item) for item in json_obj]
        return json_obj


def test_any_mode_with_one_template():
    """Test du mode 'any' : le correcteur s'active si AU MOINS UN template est présent."""
    print("\n=== Test: Mode 'any' avec un seul template présent ===")

    corrector = AnyModeCorrector()

    # Seulement "template/a" est présent (sur 3 possibles)
    template_names = {"template/a"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Correcteur avec templates {corrector.template_names}")
    print(f"Templates présents: {template_names}")
    print(f"Mode: {corrector.applicability_mode}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is True
    print("✅ PASS - Le correcteur est applicable avec au moins 1 template")


def test_any_mode_with_all_templates():
    """Test du mode 'any' : fonctionne aussi si TOUS les templates sont présents."""
    print("\n=== Test: Mode 'any' avec tous les templates présents ===")

    corrector = AnyModeCorrector()

    # Tous les templates sont présents
    template_names = {"template/a", "template/b", "template/c"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Templates présents: {template_names}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is True
    print("✅ PASS - Le correcteur est applicable avec tous les templates")


def test_any_mode_with_no_match():
    """Test du mode 'any' : non applicable si aucun template ne correspond."""
    print("\n=== Test: Mode 'any' sans aucun template correspondant ===")

    corrector = AnyModeCorrector()

    # Aucun template ne correspond
    template_names = {"other/template", "another/one"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Templates présents: {template_names}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is False
    print("✅ PASS - Le correcteur n'est pas applicable sans template correspondant")


def test_all_mode_with_one_template():
    """Test du mode 'all' : NON applicable si seulement UN template est présent."""
    print("\n=== Test: Mode 'all' avec un seul template présent ===")

    corrector = AllModeCorrector()

    # Seulement "template/x" est présent (il manque "template/y")
    template_names = {"template/x"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Correcteur avec templates {corrector.template_names}")
    print(f"Templates présents: {template_names}")
    print(f"Mode: {corrector.applicability_mode}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is False
    print("✅ PASS - Le correcteur n'est PAS applicable car tous les templates ne sont pas présents")


def test_all_mode_with_all_templates():
    """Test du mode 'all' : applicable si TOUS les templates sont présents."""
    print("\n=== Test: Mode 'all' avec tous les templates présents ===")

    corrector = AllModeCorrector()

    # Tous les templates requis sont présents
    template_names = {"template/x", "template/y"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Templates présents: {template_names}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is True
    print("✅ PASS - Le correcteur est applicable car tous les templates sont présents")


def test_all_mode_with_extra_templates():
    """Test du mode 'all' : fonctionne même avec des templates supplémentaires."""
    print("\n=== Test: Mode 'all' avec templates requis + extras ===")

    corrector = AllModeCorrector()

    # Tous les templates requis + des extras
    template_names = {"template/x", "template/y", "other/template"}

    is_applicable = corrector.is_applicable(template_names)
    print(f"Templates présents: {template_names}")
    print(f"Applicable: {is_applicable}")

    assert is_applicable is True
    print("✅ PASS - Le correcteur est applicable même avec des templates supplémentaires")


def test_integration_with_registry():
    """Test d'intégration : registry utilise is_applicable() avec les deux modes."""
    print("\n=== Test: Intégration avec CorrectorRegistry ===")

    registry = CorrectorRegistry()
    registry.register(AnyModeCorrector())
    registry.register(AllModeCorrector())

    # Scénario 1: Seulement "template/a" présent
    print("\nScénario 1: template_names = {'template/a'}")
    template_names = {"template/a"}
    applicable = registry.get_applicable_correctors(template_names)
    print(f"Correcteurs applicables: {[c.name for c in applicable]}")

    assert len(applicable) == 1
    assert applicable[0].name == "AnyModeCorrector"
    print("✅ PASS - Seul AnyModeCorrector est applicable")

    # Scénario 2: "template/x" et "template/y" présents
    print("\nScénario 2: template_names = {'template/x', 'template/y'}")
    template_names = {"template/x", "template/y"}
    applicable = registry.get_applicable_correctors(template_names)
    print(f"Correcteurs applicables: {[c.name for c in applicable]}")

    assert len(applicable) == 1
    assert applicable[0].name == "AllModeCorrector"
    print("✅ PASS - Seul AllModeCorrector est applicable")

    # Scénario 3: "template/a", "template/x" et "template/y" présents
    print("\nScénario 3: template_names = {'template/a', 'template/x', 'template/y'}")
    template_names = {"template/a", "template/x", "template/y"}
    applicable = registry.get_applicable_correctors(template_names)
    print(f"Correcteurs applicables: {[c.name for c in applicable]}")

    assert len(applicable) == 2
    assert "AnyModeCorrector" in [c.name for c in applicable]
    assert "AllModeCorrector" in [c.name for c in applicable]
    print("✅ PASS - Les deux correcteurs sont applicables")


def test_process_with_modes():
    """Test complet avec processSeriesOfCorrections et les deux modes."""
    print("\n=== Test: processSeriesOfCorrections avec modes différents ===")

    registry = CorrectorRegistry()
    registry.register(AnyModeCorrector())
    registry.register(AllModeCorrector())

    structure = [
        {
            "template_name": "template/a",
            "field_a": "bad",
        },
        {
            "template_name": "template/x",
            "field_all": "bad",
        },
        {
            "template_name": "template/y",
            "other": "data",
        },
    ]

    print("Structure avant:")
    print(f"  Item 0: template/a, field_a='bad'")
    print(f"  Item 1: template/x, field_all='bad'")
    print(f"  Item 2: template/y")

    corrected, stats = processSeriesOfCorrections(structure, registry)

    print("\nStructure après:")
    print(f"  Item 0: field_a='{corrected[0]['field_a']}'")
    print(f"  Item 1: field_all='{corrected[1]['field_all']}'")

    print(f"\nStats: {stats['corrections_by_corrector']}")

    # AnyModeCorrector devrait avoir corrigé field_a (template/a présent)
    assert corrected[0]["field_a"] == "good_any"

    # AllModeCorrector devrait avoir corrigé field_all (template/x ET template/y présents)
    assert corrected[1]["field_all"] == "good_all"

    # Les deux correcteurs devraient avoir été appliqués
    assert "AnyModeCorrector" in stats["corrections_by_corrector"]
    assert "AllModeCorrector" in stats["corrections_by_corrector"]

    print("✅ PASS - Les deux correcteurs ont été appliqués correctement selon leur mode")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTS DES MODES D'APPLICABILITÉ (ANY vs ALL)")
    print("=" * 60)

    try:
        test_any_mode_with_one_template()
        test_any_mode_with_all_templates()
        test_any_mode_with_no_match()
        test_all_mode_with_one_template()
        test_all_mode_with_all_templates()
        test_all_mode_with_extra_templates()
        test_integration_with_registry()
        test_process_with_modes()

        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("=" * 60 + "\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
