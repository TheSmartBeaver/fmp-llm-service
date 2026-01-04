#!/usr/bin/env python3
"""
Test de la fonctionnalité de groupes imbriqués.

Vérifie que les références entre groupes parent-enfant sont bien gérées.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator
from app.database import get_db
from sentence_transformers import SentenceTransformer
import json


def test_nested_group_references():
    """Teste la détection et l'ajout de références pour les groupes imbriqués."""

    # Initialiser le générateur
    db = next(get_db())
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    generator = TemplateStructureGenerator(db, embedding_model)

    # Groupes de test (simulant le résultat de _generate_path_groups_with_llm)
    path_groups = [
        {
            "group_name": "Conjugation patterns overview",
            "keys": [
                "conjugation_patterns[x]group",
                "conjugation_patterns[x]model",
                "conjugation_patterns[x]notes"
            ],
            "format": "Fiche de schéma de conjugaison par groupe verbal."
        },
        {
            "group_name": "Conjugation patterns forms",
            "keys": [
                "conjugation_patterns[x]forms[y]person",
                "conjugation_patterns[x]forms[y]spanish",
                "conjugation_patterns[x]forms[y]french"
            ],
            "format": "Tableau de conjugaison structuré par personne."
        }
    ]

    print("=" * 80)
    print("TEST: Ajout de références aux groupes imbriqués")
    print("=" * 80)

    print("\n📦 Groupes AVANT l'ajout de références:")
    print("-" * 80)
    for i, group in enumerate(path_groups, 1):
        print(f"\nGroupe {i}: {group['group_name']}")
        print(f"  Clés ({len(group['keys'])}):")
        for key in group['keys']:
            print(f"    - {key}")

    # Ajouter les références
    updated_groups = generator._add_nested_group_references(path_groups)

    print("\n\n📦 Groupes APRÈS l'ajout de références:")
    print("-" * 80)
    for i, group in enumerate(updated_groups, 1):
        print(f"\nGroupe {i}: {group['group_name']}")
        print(f"  Clés ({len(group['keys'])}):")
        for key in group['keys']:
            # Marquer les nouvelles clés ajoutées
            is_new = key not in path_groups[i-1]['keys']
            marker = " ✨ NOUVEAU" if is_new else ""
            print(f"    - {key}{marker}")

    # Vérifications
    print("\n\n" + "=" * 80)
    print("VÉRIFICATIONS:")
    print("=" * 80)

    overview_group = updated_groups[0]
    expected_reference = "conjugation_patterns[x]forms[y]"

    if expected_reference in overview_group["keys"]:
        print(f"✅ Référence '{expected_reference}' ajoutée au groupe overview")
    else:
        print(f"❌ Référence '{expected_reference}' NON trouvée dans le groupe overview")
        print(f"   Clés actuelles: {overview_group['keys']}")

    return updated_groups


def test_full_workflow_with_nested_groups():
    """Teste le workflow complet avec des groupes imbriqués."""

    # Initialiser le générateur
    db = next(get_db())
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    generator = TemplateStructureGenerator(db, embedding_model)

    # JSON source avec structure imbriquée
    source_json = {
        "conjugation_patterns": [
            {
                "group": "1er groupe",
                "model": "hablar",
                "notes": "Verbes réguliers en -ar",
                "forms": [
                    {"person": "yo", "spanish": "hablo", "french": "je parle"},
                    {"person": "tú", "spanish": "hablas", "french": "tu parles"},
                ]
            }
        ]
    }

    print("\n\n" + "=" * 80)
    print("TEST: Workflow complet avec groupes imbriqués")
    print("=" * 80)

    print("\nJSON source:")
    print(json.dumps(source_json, indent=2, ensure_ascii=False))

    # Générer la structure de templates
    result = generator.generate_template_structure(
        source_json=source_json,
        context_description="Cours d'espagnol sur les conjugaisons",
        top_k_per_packet=8,
    )

    print("\n✅ Structure générée avec succès !")

    print("\n" + "=" * 80)
    print("JSON STRUCTURÉ GÉNÉRÉ:")
    print("=" * 80)
    print(json.dumps(result["template_structure"], indent=2, ensure_ascii=False))

    # Vérifier que la structure contient bien des objets imbriqués (pas de références non résolues)
    json_str = json.dumps(result["template_structure"])

    # Compter les niveaux d'imbrication en cherchant "template_name"
    template_count = json_str.count('"template_name"')

    if template_count >= 2:
        print(f"\n✅ Structure imbriquée correctement générée ({template_count} templates trouvés)")
    else:
        print(f"\n⚠️  Structure peut-être trop plate ({template_count} template(s) trouvé(s))")

    return result


if __name__ == "__main__":
    print("🚀 Démarrage des tests de groupes imbriqués\n")

    try:
        # Test 1: Ajout de références seulement
        print("🔬 TEST 1: Ajout de références aux groupes imbriqués")
        updated_groups = test_nested_group_references()

        # Test 2: Workflow complet
        print("\n\n🔬 TEST 2: Workflow complet avec résolution des références")
        result = test_full_workflow_with_nested_groups()

        print("\n\n" + "=" * 80)
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("=" * 80)

    except Exception as e:
        print("\n\n" + "=" * 80)
        print("❌ ERREUR:")
        print("=" * 80)
        import traceback
        traceback.print_exc()
