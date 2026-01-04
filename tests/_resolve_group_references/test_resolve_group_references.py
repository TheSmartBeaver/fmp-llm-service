"""
Test pour vérifier que _resolve_group_references utilise bien path_to_value_map
pour vérifier que toutes les clés nécessaires sont créées.
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator


# Données de test : un JSON pédagogique simple
test_pedagogical_json = {
    "course": "Français",
    "glossary": [
        {
            "term": "Auxiliaire",
            "definition": "Verbe être ou avoir"
        },
        {
            "term": "Participe passé",
            "definition": "Forme du verbe"
        }
    ]
}

# Données de test : group_jsons_map simulé (ce que le LLM aurait généré)
# Ce test simule un cas où le LLM a OUBLIÉ de créer certaines clés
test_group_jsons_map_incomplete = {
    "course": "{{course}}",
    "glossary[x]": {
        "items": [
            {
                "glossary[x]->term": "{{glossary[x]->term}}"
                # MANQUE: glossary[x]->definition
            }
        ]
    }
}

# Données de test : group_jsons_map complet
test_group_jsons_map_complete = {
    "course": "{{course}}",
    "glossary[x]": {
        "items": [
            {
                "glossary[x]->term": "{{glossary[x]->term}}",
                "glossary[x]->definition": "{{glossary[x]->definition}}"
            }
        ]
    }
}


def test_resolve_group_references_incomplete():
    """Test avec un group_jsons_map incomplet (clés manquantes)."""
    print("=" * 80)
    print("TEST 1: group_jsons_map INCOMPLET (devrait afficher un avertissement)")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Construire path_to_value_map
    path_to_value_map = generator._build_path_to_value_map(test_pedagogical_json)

    print(f"\nClés dans path_to_value_map: {sorted(path_to_value_map.keys())}")
    print(f"Nombre de clés: {len(path_to_value_map)}")

    # Résoudre les références (devrait afficher un avertissement)
    print("\nAppel de _resolve_group_references avec group_jsons_map incomplet:")
    print("-" * 80)
    resolved = generator._resolve_group_references(test_group_jsons_map_incomplete, path_to_value_map)

    print("\n" + "=" * 80)
    print()


def test_resolve_group_references_complete():
    """Test avec un group_jsons_map complet (toutes les clés présentes)."""
    print("=" * 80)
    print("TEST 2: group_jsons_map COMPLET (devrait afficher ✅)")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Construire path_to_value_map
    path_to_value_map = generator._build_path_to_value_map(test_pedagogical_json)

    print(f"\nClés dans path_to_value_map: {sorted(path_to_value_map.keys())}")
    print(f"Nombre de clés: {len(path_to_value_map)}")

    # Résoudre les références (ne devrait PAS afficher d'avertissement)
    print("\nAppel de _resolve_group_references avec group_jsons_map complet:")
    print("-" * 80)
    resolved = generator._resolve_group_references(test_group_jsons_map_complete, path_to_value_map)

    print("\n" + "=" * 80)
    print()


if __name__ == "__main__":
    test_resolve_group_references_incomplete()
    print("\n\n")
    test_resolve_group_references_complete()
    print("\n✅ Tests terminés!")
