#!/usr/bin/env python3
"""
Test that the double index bug fix works correctly.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_double_index_fix():
    """Test that auto-fix doesn't create double indices"""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Create a scenario that would produce double indices WITHOUT the fix
    print("=" * 80)
    print("TEST: Auto-fix should not create double indices")
    print("=" * 80)

    # This conflict pattern could potentially create double indices
    source_paths = [
        "items[x]subitems[y]name",
        "items[x]subitems[y]value",
    ]

    # Simulate problematic mappings that share a prefix ending with an index
    mappings_with_potential_double_index = {
        "items[x]subitems[y]name": 'container["items"][x]["subitems"][y]text/name["text"]',
        "items[x]subitems[y]value": 'container["items"][x]["subitems"][y]text/value["text"]',
    }

    print("\n❌ AVANT correction:")
    for src, dest in mappings_with_potential_double_index.items():
        print(f'  "{src}": \'{dest}\'')

    # Detect conflicts
    errors_before = generator._validate_destination_mappings(mappings_with_potential_double_index)
    print(f"\nErreurs détectées AVANT: {len(errors_before)}")
    if errors_before:
        for err in errors_before:
            print(f"  {err}")

    # Apply auto-fix
    fixed_mappings = generator._auto_fix_overlaps(mappings_with_potential_double_index, source_paths)

    print("\n✅ APRÈS correction:")
    for src, dest in fixed_mappings.items():
        print(f'  "{src}": \'{dest}\'')

    # Check for double indices in the fixed mappings
    has_double_index = False
    for src, dest in fixed_mappings.items():
        segments = generator._parse_destination_path(dest)
        for i in range(len(segments) - 1):
            if segments[i]["type"] == "index" and segments[i+1]["type"] == "index":
                print(f"\n⚠️  DOUBLE INDEX DETECTED in '{src}':")
                print(f"    Path: {dest}")
                print(f"    Segments {i} and {i+1}: {segments[i]} -> {segments[i+1]}")
                has_double_index = True

    if not has_double_index:
        print("\n✅ No double indices found - FIX SUCCESSFUL!")
    else:
        print("\n❌ Double indices still present - FIX FAILED!")

    # Validate after correction
    errors_after = generator._validate_destination_mappings(fixed_mappings)
    print(f"\nErreurs de validation APRÈS: {len(errors_after)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_double_index_fix()
