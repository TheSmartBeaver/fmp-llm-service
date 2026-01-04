#!/usr/bin/env python3
"""
Script de test pour la nouvelle approche de génération de structure de templates.

Teste la méthode _generate_path_groups_with_llm qui remplace _generate_destination_paths_with_llm.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator
from app.database import get_db
from sentence_transformers import SentenceTransformer


def test_path_groups_generation():
    """Teste la génération de groupes de chemins avec formats."""

    # Initialiser le générateur
    db = next(get_db())
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    generator = TemplateStructureGenerator(db, embedding_model)

    # Chemins de test (exemple de cours d'espagnol)
    source_paths = [
        "learning_objective",
        "course_sections[x]section_title",
        "course_sections[x]section_description",
        "course_sections[x]key_concepts[y]concept_name",
        "course_sections[x]key_concepts[y]explanation",
        "course_sections[x]key_concepts[y]examples",
        "course_sections[x]additional_notes",
    ]

    context_description = "Cours d'espagnol sur les verbes"

    print("=" * 80)
    print("TEST: Génération des groupes de chemins")
    print("=" * 80)
    print(f"\nChemin sources:\n{chr(10).join(['  - ' + p for p in source_paths])}")
    print(f"\nContexte: {context_description}")
    print("\n" + "-" * 80)

    # Appeler la nouvelle méthode
    path_groups = generator._generate_path_groups_with_llm(
        source_paths=source_paths,
        context_description=context_description,
    )

    print("\nGroupes générés:")
    print("=" * 80)

    for i, group in enumerate(path_groups, 1):
        print(f"\n📦 Groupe {i}: {group['group_name']}")
        print(f"   Format: {group['format']}")
        print(f"   Clés ({len(group['keys'])}):")
        for key in group['keys']:
            print(f"     - {key}")

    print("\n" + "=" * 80)
    print(f"✅ Test réussi ! {len(path_groups)} groupe(s) généré(s)")
    print("=" * 80)

    return path_groups


def test_full_workflow():
    """Teste le workflow complet avec un JSON source."""

    # Initialiser le générateur
    db = next(get_db())
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    generator = TemplateStructureGenerator(db, embedding_model)

    # JSON source de test
    source_json = {
        "learning_objective": "Maîtriser les verbes irréguliers en espagnol",
        "course_sections": [
            {
                "section_title": "Verbes en -AR",
                "section_description": "Introduction aux verbes en -AR",
                "key_concepts": [
                    {
                        "concept_name": "Conjugaison présent",
                        "explanation": "Comment conjuguer au présent",
                        "examples": ["Yo hablo", "Tú hablas"],
                    }
                ],
                "additional_notes": "Pratiquer régulièrement",
            }
        ],
    }

    print("\n" + "=" * 80)
    print("TEST: Workflow complet")
    print("=" * 80)

    # Générer la structure de templates
    result = generator.generate_template_structure(
        source_json=source_json,
        context_description="Cours d'espagnol sur les verbes",
        top_k_per_packet=8,
    )

    print("\n✅ Structure générée avec succès !")

    # Afficher le JSON structuré généré
    import json
    print("\n" + "=" * 80)
    print("JSON STRUCTURÉ GÉNÉRÉ:")
    print("=" * 80)
    print(json.dumps(result["template_structure"], indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    print("🚀 Démarrage des tests de la nouvelle approche\n")

    try:
        # Test 1: Génération de groupes seulement
        print("\n" + "🔬 TEST 1: Génération de groupes")
        path_groups = test_path_groups_generation()

        # Test 2: Workflow complet
        print("\n\n" + "🔬 TEST 2: Workflow complet")
        result = test_full_workflow()

        print("\n\n" + "=" * 80)
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("=" * 80)

    except Exception as e:
        print("\n\n" + "=" * 80)
        print("❌ ERREUR:")
        print("=" * 80)
        import traceback
        traceback.print_exc()
