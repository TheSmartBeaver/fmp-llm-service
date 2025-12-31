#!/usr/bin/env python3
"""
Script de test pour vérifier la boucle de correction des destination_mappings.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator


def test_validate_destination_mappings():
    """Teste la validation avec des mappings invalides."""

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Test 1: Conflit sur un index [y] - templates différents
    print("=" * 80)
    print("TEST 1: Conflit sur l'index [y]")
    print("=" * 80)

    mappings_test1 = {
        "key_concepts[y]name": 'container["items"][y]conceptual/concept["title"]',
        "key_concepts[y]examples": 'container["items"][y]text/liste_exemples["items"]',
    }

    errors = generator._validate_destination_mappings(mappings_test1)
    print(f"Nombre d'erreurs détectées: {len(errors)}")
    for error in errors:
        print(f"\n{error}")

    # Test 2: Conflit sur un champ ["content"] - templates différents
    print("\n" + "=" * 80)
    print("TEST 2: Conflit sur le champ [\"content\"]")
    print("=" * 80)

    mappings_test2 = {
        "section_description": 'item["content"]text/description["text"]',
        "key_concepts[y]name": 'item["content"]layouts/container["items"][y]conceptual/concept["title"]',
    }

    errors = generator._validate_destination_mappings(mappings_test2)
    print(f"Nombre d'erreurs détectées: {len(errors)}")
    for error in errors:
        print(f"\n{error}")

    # Test 3: Mappings valides - pas d'erreur
    print("\n" + "=" * 80)
    print("TEST 3: Mappings VALIDES (pas d'erreur attendue)")
    print("=" * 80)

    mappings_test3 = {
        "key_concepts[y]name": 'container["items"][y]conceptual/concept["title"]',
        "key_concepts[y]explanation": 'container["items"][y]conceptual/concept["description"]',
        "key_concepts[y]examples": 'container["items"][y]conceptual/concept["examples"]',
    }

    errors = generator._validate_destination_mappings(mappings_test3)
    print(f"Nombre d'erreurs détectées: {len(errors)}")
    if errors:
        for error in errors:
            print(f"\n{error}")
    else:
        print("✅ Aucune erreur détectée (comme attendu)")

    # Test 4: L'exemple problématique de l'utilisateur
    print("\n" + "=" * 80)
    print("TEST 4: Exemple problématique de l'utilisateur")
    print("=" * 80)

    mappings_test4 = {
        "learning_objective": 'layouts/vertical_column/container["items"][0]text/description_longue["text"]',
        "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["title"]text/titre_secondaire["text"]',
        "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]text/description_longue["text"]',
        "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]conceptual/concept["title"]',
        "course_sections[x]key_concepts[y]explanation": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]conceptual/concept["description"]',
        "course_sections[x]key_concepts[y]examples": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/grid/container["items"][y]text/liste_exemples["items"]',
        "course_sections[x]key_concepts[y]related_media": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/grid/container["items"][y]text/detail_technique["text"]',
        "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]text/contexte["text"]',
    }

    errors = generator._validate_destination_mappings(mappings_test4)
    print(f"Nombre d'erreurs détectées: {len(errors)}")
    for error in errors:
        print(f"\n{error}")

    print("\n" + "=" * 80)
    print("Tests terminés!")
    print("=" * 80)


if __name__ == "__main__":
    test_validate_destination_mappings()
