#!/usr/bin/env python3
"""
Script de debug pour comprendre pourquoi _auto_fix_overlaps ne fonctionne pas.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_debug():
    """Teste étape par étape l'algorithme de correction."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Test simple: 2 chemins en conflit
    source_paths = [
        "course_sections[x]section_description",
        "course_sections[x]key_concepts[y]concept_name",
    ]

    mappings = {
        "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]concept["title"]',
    }

    print("=" * 80)
    print("ÉTAPE 1: Regroupement des chemins sources")
    print("=" * 80)
    groups = generator._group_source_paths_by_prefix(source_paths)
    for group_key, paths in groups.items():
        print(f"\nGroupe '{group_key}':")
        for p in paths:
            print(f"  - {p}")

    print("\n" + "=" * 80)
    print("ÉTAPE 2: Vérification des chevauchements par groupe")
    print("=" * 80)
    for group_key, paths_in_group in groups.items():
        dest_paths = {src: mappings.get(src) for src in paths_in_group if src in mappings}

        print(f"\nGroupe '{group_key}':")
        print(f"Chemins de destination:")
        for src, dest in dest_paths.items():
            print(f"  {src}: {dest}")

        has_overlap = generator._group_has_overlap(dest_paths)
        print(f"A des chevauchements: {has_overlap}")

        if has_overlap:
            print("\n>>> Application de la stratégie des indices fixes...")

            # Parser les chemins
            print("\nParsing des chemins de destination:")
            for src, dest in dest_paths.items():
                segments = generator._parse_destination_path(dest)
                print(f"\n  {src}:")
                for i, seg in enumerate(segments):
                    print(f"    [{i}] {seg}")

            # Appliquer la correction
            fixed_group = generator._apply_fixed_index_strategy(dest_paths, group_key)

            print("\nRésultat après correction:")
            for src, dest in fixed_group.items():
                print(f"  {src}: {dest}")

    print("\n" + "=" * 80)
    print("ÉTAPE 3: Résultat final de _auto_fix_overlaps")
    print("=" * 80)
    result = generator._auto_fix_overlaps(mappings, source_paths)
    for src, dest in result.items():
        print(f"{src}: {dest}")

    print("\n" + "=" * 80)
    print("ÉTAPE 4: Validation du résultat")
    print("=" * 80)
    errors = generator._validate_destination_mappings(result)
    print(f"Nombre d'erreurs: {len(errors)}")
    for err in errors:
        print(f"  - {err}")


if __name__ == "__main__":
    test_debug()
