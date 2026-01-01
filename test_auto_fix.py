#!/usr/bin/env python3
"""
Script de test pour vérifier la correction automatique des chevauchements.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_auto_fix_overlaps():
    """Teste la correction automatique des chevauchements."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Test 1: Conflit typique sur ["content"]
    print("=" * 80)
    print("TEST 1: Conflit sur le champ [\"content\"]")
    print("=" * 80)

    source_paths = [
        "course_sections[x]section_description",
        "course_sections[x]key_concepts[y]concept_name",
    ]

    mappings_with_conflict = {
        "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]concept["title"]',
    }

    print("\n❌ AVANT correction:")
    for src, dest in mappings_with_conflict.items():
        print(f'  "{src}": \'{dest}\'')

    # Validation avant
    errors_before = generator._validate_destination_mappings(mappings_with_conflict)
    print(f"\nErreurs détectées AVANT: {len(errors_before)}")
    for err in errors_before:
        print(f"  - {err[:100]}...")

    # Correction automatique
    fixed_mappings = generator._auto_fix_overlaps(mappings_with_conflict, source_paths)

    print("\n✅ APRÈS correction:")
    for src, dest in fixed_mappings.items():
        print(f'  "{src}": \'{dest}\'')

    # Validation après
    errors_after = generator._validate_destination_mappings(fixed_mappings)
    print(f"\nErreurs détectées APRÈS: {len(errors_after)}")
    if errors_after:
        for err in errors_after:
            print(f"  - {err[:100]}...")
    else:
        print("  ✅ Aucune erreur ! Correction réussie.")

    # Test 2: Exemple complet avec multiples conflits
    print("\n" + "=" * 80)
    print("TEST 2: Exemple complet avec multiples chemins")
    print("=" * 80)

    source_paths_2 = [
        "learning_objective",
        "course_sections[x]section_title",
        "course_sections[x]section_description",
        "course_sections[x]key_concepts[y]concept_name",
        "course_sections[x]additional_notes",
    ]

    mappings_with_conflict_2 = {
        "learning_objective": 'layouts/vertical_column/container["items"][0]text/description["text"]',
        "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["title"]text/titre["text"]',
        "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]layouts/container["items"][y]conceptual/concept["title"]',
        "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]text/notes["text"]',
    }

    print("\n❌ AVANT correction:")
    for src, dest in mappings_with_conflict_2.items():
        print(f'  "{src}": \'{dest}\'')

    errors_before_2 = generator._validate_destination_mappings(mappings_with_conflict_2)
    print(f"\nErreurs détectées AVANT: {len(errors_before_2)}")

    fixed_mappings_2 = generator._auto_fix_overlaps(mappings_with_conflict_2, source_paths_2)

    print("\n✅ APRÈS correction:")
    for src, dest in fixed_mappings_2.items():
        print(f'  "{src}": \'{dest}\'')

    errors_after_2 = generator._validate_destination_mappings(fixed_mappings_2)
    print(f"\nErreurs détectées APRÈS: {len(errors_after_2)}")
    if errors_after_2:
        for err in errors_after_2:
            print(f"  - {err[:100]}...")
    else:
        print("  ✅ Aucune erreur ! Correction réussie.")

    print("\n" + "=" * 80)
    print("Tests terminés!")
    print("=" * 80)


if __name__ == "__main__":
    test_auto_fix_overlaps()
