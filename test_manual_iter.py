#!/usr/bin/env python3
"""
Test manuel itération par itération.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_manual_iterations():
    """Teste manuellement chaque itération."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    mappings = {
        "learning_objective": 'layouts/vertical_column/container["items"][0]text/description["text"]',
        "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["title"]text/titre["text"]',
        "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]["content"]layouts/container["items"][y]conceptual/concept["title"]',
        "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][1]layouts/item["items"][x]text/notes["text"]',
    }

    current = dict(mappings)

    for iteration in range(5):
        print("=" * 80)
        print(f"ITÉRATION {iteration + 1}")
        print("=" * 80)

        conflicts = generator._detect_destination_conflicts(current)
        print(f"\nConflits détectés: {len(conflicts)}")

        if not conflicts:
            print("✅ Plus de conflits!")
            break

        for prefix, sources in conflicts.items():
            print(f"\nPréfixe: {prefix}")
            print(f"Sources: {', '.join(sources)}")

            # Appliquer la correction
            dest_paths = {src: current[src] for src in sources}
            fixed_group = generator._apply_fixed_index_strategy(dest_paths, prefix)

            print("\nCorrection appliquée:")
            for src, dest in fixed_group.items():
                print(f"  {src}:")
                print(f"    AVANT: {current[src]}")
                print(f"    APRÈS: {dest}")

            # Mettre à jour
            current.update(fixed_group)

        print("\nÉtat après correction:")
        for src, dest in sorted(current.items()):
            print(f"  {src}: {dest}")


if __name__ == "__main__":
    test_manual_iterations()
