#!/usr/bin/env python3
"""
Test de la détection de conflits au niveau destination.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_conflict_detection():
    """Teste la détection de conflits."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    mappings = {
        "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]concept["title"]',
    }

    print("=" * 80)
    print("Test de _detect_destination_conflicts")
    print("=" * 80)
    print("\nMappings:")
    for src, dest in mappings.items():
        print(f"  {src}:")
        print(f"    -> {dest}")

    conflicts = generator._detect_destination_conflicts(mappings)

    print(f"\nNombre de conflits détectés: {len(conflicts)}")
    for prefix, sources in conflicts.items():
        print(f"\nPréfixe en conflit: {prefix}")
        print(f"Chemins sources concernés:")
        for src in sources:
            print(f"  - {src}")


if __name__ == "__main__":
    test_conflict_detection()
