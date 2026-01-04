#!/usr/bin/env python3
"""
Test to reproduce the double index bug
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_double_index_parsing():
    """Test parsing of paths with double indices"""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # This is the problematic path from the error message
    problematic_path = 'layouts/vertical_column/container["items"][1][4]layouts/vertical_column/item["content"]conceptual/concept["description"]'

    print("Testing path parsing with double index:")
    print(f"Path: {problematic_path}")
    print()

    segments = generator._parse_destination_path(problematic_path)

    print("Parsed segments:")
    for i, seg in enumerate(segments):
        print(f"  {i}: {seg}")
    print()

    # Check for consecutive index segments
    for i in range(len(segments) - 1):
        if segments[i]["type"] == "index" and segments[i+1]["type"] == "index":
            print(f"⚠️  FOUND DOUBLE INDEX at positions {i} and {i+1}")
            print(f"    {segments[i]} -> {segments[i+1]}")
            print()

    # Test insertion
    print("Testing insertion into structure:")
    result = {}
    try:
        generator._insert_value_in_structure(result, segments, "test value")
        print("✅ Insertion succeeded")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Insertion failed: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_double_index_parsing()
