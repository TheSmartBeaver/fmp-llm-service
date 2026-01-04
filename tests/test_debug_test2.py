#!/usr/bin/env python3
"""
Debug du Test 2 qui échoue.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_debug_test2():
    """Debug le test 2."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    mappings_test2 = {
        "learning_objective": 'layouts/vertical_column/container["items"][0]text/description["text"]',
        "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["title"]text/titre["text"]',
        "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]layouts/container["items"][y]conceptual/concept["title"]',
        "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]text/notes["text"]',
    }

    print("=" * 80)
    print("AVANT correction")
    print("=" * 80)
    for src, dest in mappings_test2.items():
        print(f"{src}:")
        print(f"  {dest}")

    conflicts = generator._detect_destination_conflicts(mappings_test2)
    print(f"\nConflits détectés: {len(conflicts)}")
    for prefix, sources in conflicts.items():
        print(f"\nPréfixe: {prefix}")
        print(f"Sources:")
        for src in sources:
            print(f"  - {src}")

    print("\n" + "=" * 80)
    print("APRÈS correction auto-fix (itératif)")
    print("=" * 80)

    fixed = generator._auto_fix_overlaps(mappings_test2, list(mappings_test2.keys()))

    for src, dest in fixed.items():
        print(f"{src}:")
        print(f"  {dest}")

    conflicts_after = generator._detect_destination_conflicts(fixed)
    print(f"\nConflits détectés après: {len(conflicts_after)}")
    for prefix, sources in conflicts_after.items():
        print(f"\nPréfixe: {prefix}")
        print(f"Sources:")
        for src in sources:
            print(f"  - {src}")


if __name__ == "__main__":
    test_debug_test2()
