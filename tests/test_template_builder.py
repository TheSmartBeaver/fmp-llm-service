"""
Script de test pour valider la construction du JSON final
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator

def test_conversion_indices_to_variables():
    """Test de la conversion d'indices en variables"""
    gen = TemplateStructureGenerator(None, None)

    # Test 1: chemin simple avec un index
    path, mapping = gen._convert_indices_to_variables("course_sections[0]title")
    assert path == "course_sections[x]title", f"Expected 'course_sections[x]title', got '{path}'"
    assert mapping == {'x': 0}, f"Expected {{'x': 0}}, got {mapping}"
    print("✓ Test 1 passed: simple path with one index")

    # Test 2: chemin avec deux indices
    path, mapping = gen._convert_indices_to_variables("course_sections[2]lessons[3]title")
    assert path == "course_sections[x]lessons[y]title", f"Expected 'course_sections[x]lessons[y]title', got '{path}'"
    assert mapping == {'x': 2, 'y': 3}, f"Expected {{'x': 2, 'y': 3}}, got {mapping}"
    print("✓ Test 2 passed: path with two indices")

    # Test 3: chemin sans index
    path, mapping = gen._convert_indices_to_variables("learning_objective")
    assert path == "learning_objective", f"Expected 'learning_objective', got '{path}'"
    assert mapping == {}, f"Expected {{}}, got {mapping}"
    print("✓ Test 3 passed: path without index")

def test_substitute_variables():
    """Test de la substitution des variables"""
    gen = TemplateStructureGenerator(None, None)

    # Test 1: substitution simple
    result = gen._substitute_variables_in_destination(
        'container["items"][x]concept["title"]',
        {'x': 0}
    )
    assert result == 'container["items"][0]concept["title"]', f"Expected 'container[\"items\"][0]concept[\"title\"]', got '{result}'"
    print("✓ Test 4 passed: simple variable substitution")

    # Test 2: substitution multiple
    result = gen._substitute_variables_in_destination(
        'container["items"][x]nested["items"][y]concept["title"]',
        {'x': 2, 'y': 5}
    )
    assert result == 'container["items"][2]nested["items"][5]concept["title"]', f"Got '{result}'"
    print("✓ Test 5 passed: multiple variable substitution")

def test_parse_destination_path():
    """Test du parser de chemin de destination"""
    gen = TemplateStructureGenerator(None, None)

    # Test 1: parsing simple
    segments = gen._parse_destination_path('layouts/vertical_column/container["items"][0]conceptual/concept["title"]')

    expected = [
        {"type": "template", "value": "layouts/vertical_column/container"},
        {"type": "field", "value": "items"},
        {"type": "index", "value": 0},
        {"type": "template", "value": "conceptual/concept"},
        {"type": "field", "value": "title"}
    ]

    assert segments == expected, f"Expected {expected}, got {segments}"
    print("✓ Test 6 passed: destination path parsing")

def test_get_value_from_path():
    """Test de récupération de valeur depuis un chemin"""
    gen = TemplateStructureGenerator(None, None)

    # Données de test
    data = {
        "learning_objective": "Learn Spanish verbs",
        "course_sections": [
            {
                "section_id": "sec1",
                "lessons": [
                    {"title": "Lesson 1.1"},
                    {"title": "Lesson 1.2"}
                ]
            },
            {
                "section_id": "sec2",
                "lessons": [
                    {"title": "Lesson 2.1"}
                ]
            }
        ]
    }

    # Test 1: valeur simple
    value = gen._get_value_from_path(data, "learning_objective")
    assert value == "Learn Spanish verbs", f"Expected 'Learn Spanish verbs', got '{value}'"
    print("✓ Test 7 passed: get simple value")

    # Test 2: valeur avec index
    value = gen._get_value_from_path(data, "course_sections[1]section_id")
    assert value == "sec2", f"Expected 'sec2', got '{value}'"
    print("✓ Test 8 passed: get value with one index")

    # Test 3: valeur avec indices imbriqués
    value = gen._get_value_from_path(data, "course_sections[0]lessons[1]title")
    assert value == "Lesson 1.2", f"Expected 'Lesson 1.2', got '{value}'"
    print("✓ Test 9 passed: get value with nested indices")

def test_insert_value_simple():
    """Test d'insertion de valeur simple"""
    gen = TemplateStructureGenerator(None, None)

    result = {}
    segments = [
        {"type": "template", "value": "conceptual/concept"},
        {"type": "field", "value": "title"}
    ]

    gen._insert_value_in_structure(result, segments, "My Title")

    expected = {
        "template_name": "conceptual/concept",
        "title": "My Title"
    }

    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Test 10 passed: insert simple value")

def test_insert_value_with_array():
    """Test d'insertion avec tableau"""
    gen = TemplateStructureGenerator(None, None)

    result = {}

    # Insérer dans un tableau à l'index 0
    segments = [
        {"type": "template", "value": "layouts/container"},
        {"type": "field", "value": "items"},
        {"type": "index", "value": 0},
        {"type": "template", "value": "conceptual/concept"},
        {"type": "field", "value": "title"}
    ]

    gen._insert_value_in_structure(result, segments, "First Item")

    expected = {
        "template_name": "layouts/container",
        "items": [
            {
                "template_name": "conceptual/concept",
                "title": "First Item"
            }
        ]
    }

    assert result == expected, f"Expected {json.dumps(expected, indent=2)}, got {json.dumps(result, indent=2)}"
    print("✓ Test 11 passed: insert value with array")

    # Insérer un deuxième élément
    segments[2]["value"] = 1  # index 1
    gen._insert_value_in_structure(result, segments, "Second Item")

    expected["items"].append({
        "template_name": "conceptual/concept",
        "title": "Second Item"
    })

    assert result == expected, f"Expected {json.dumps(expected, indent=2)}, got {json.dumps(result, indent=2)}"
    print("✓ Test 12 passed: insert second item in array")

def test_insert_complex_values():
    """Test d'insertion de valeurs complexes (objets et tableaux)"""
    gen = TemplateStructureGenerator(None, None)

    result = {}

    # Test avec un objet complexe comme valeur
    segments = [
        {"type": "template", "value": "conceptual/concept"},
        {"type": "field", "value": "metadata"}
    ]

    complex_object = {
        "author": "Alice",
        "tags": ["spanish", "verbs"],
        "difficulty": 3
    }

    gen._insert_value_in_structure(result, segments, complex_object)

    expected = {
        "template_name": "conceptual/concept",
        "metadata": {
            "author": "Alice",
            "tags": ["spanish", "verbs"],
            "difficulty": 3
        }
    }

    assert result == expected, f"Expected {json.dumps(expected, indent=2)}, got {json.dumps(result, indent=2)}"
    print("✓ Test 13 passed: insert complex object value")

    # Test avec un tableau comme valeur
    result2 = {}
    segments2 = [
        {"type": "template", "value": "layouts/container"},
        {"type": "field", "value": "options"}
    ]

    array_value = ["option1", "option2", "option3"]

    gen._insert_value_in_structure(result2, segments2, array_value)

    expected2 = {
        "template_name": "layouts/container",
        "options": ["option1", "option2", "option3"]
    }

    assert result2 == expected2, f"Expected {json.dumps(expected2, indent=2)}, got {json.dumps(result2, indent=2)}"
    print("✓ Test 14 passed: insert array value")

if __name__ == "__main__":
    print("Running tests...\n")

    try:
        test_conversion_indices_to_variables()
        print()

        test_substitute_variables()
        print()

        test_parse_destination_path()
        print()

        test_get_value_from_path()
        print()

        test_insert_value_simple()
        print()

        test_insert_value_with_array()
        print()

        test_insert_complex_values()
        print()

        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
