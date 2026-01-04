#!/usr/bin/env python3
"""
Test de la règle de profondeur stricte dans le regroupement.

Vérifie que les chemins avec des profondeurs différentes sont TOUJOURS dans des groupes séparés.
"""

from app.chains.template_structure_generator import TemplateStructureGenerator
from app.database import get_db
from sentence_transformers import SentenceTransformer
import re


def count_variables(path: str) -> int:
    """Compte le nombre de variables [x], [y], [z] dans un chemin."""
    return len(re.findall(r'\[[x-z]\]', path))


def test_depth_grouping():
    """Teste que les groupes respectent la règle de profondeur stricte."""

    # Initialiser le générateur
    db = next(get_db())
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    generator = TemplateStructureGenerator(db, embedding_model)

    # Chemins de test avec différentes profondeurs
    source_paths = [
        # Profondeur 1 (1 variable)
        "conjugationTables[x]group",
        "conjugationTables[x]modelInfinitive",
        "conjugationTables[x]endingsExplanation",
        # Profondeur 2 (2 variables)
        "conjugationTables[x]conjugations[y]form",
        "conjugationTables[x]conjugations[y]personFrench",
        "conjugationTables[x]conjugations[y]personSpanish",
        "conjugationTables[x]conjugations[y]literalTranslation",
    ]

    print("=" * 80)
    print("TEST: Regroupement strict par profondeur")
    print("=" * 80)

    print("\nChemins source avec profondeurs:")
    print("-" * 80)
    for path in source_paths:
        depth = count_variables(path)
        print(f"  [Profondeur {depth}] {path}")

    # Générer les groupes
    print("\n\nGénération des groupes avec le LLM...")
    path_groups = generator._generate_path_groups_with_llm(
        source_paths=source_paths,
        context_description="Tables de conjugaison espagnole",
    )

    print("\n✅ Groupes générés:")
    print("=" * 80)

    all_valid = True
    for i, group in enumerate(path_groups, 1):
        print(f"\n📦 Groupe {i}: {group['group_name']}")
        print(f"   Format: {group['format']}")
        print(f"   Clés ({len(group['keys'])}):")

        # Vérifier que toutes les clés ont la même profondeur
        depths = [count_variables(key) for key in group['keys']]
        unique_depths = set(depths)

        for key in group['keys']:
            depth = count_variables(key)
            print(f"     [Prof. {depth}] {key}")

        # Validation
        if len(unique_depths) == 1:
            print(f"   ✅ VALIDE - Toutes les clés ont la même profondeur ({unique_depths.pop()})")
        else:
            print(f"   ❌ INVALIDE - Profondeurs mixtes: {unique_depths}")
            all_valid = False

    print("\n\n" + "=" * 80)
    print("RÉSULTAT FINAL:")
    print("=" * 80)

    if all_valid:
        print("✅ TOUS LES GROUPES RESPECTENT LA RÈGLE DE PROFONDEUR STRICTE")
    else:
        print("❌ CERTAINS GROUPES VIOLENT LA RÈGLE DE PROFONDEUR")
        print("   Le LLM a mélangé des profondeurs différentes dans un même groupe")

    return path_groups, all_valid


if __name__ == "__main__":
    print("🚀 Test de validation de la règle de profondeur stricte\n")

    try:
        path_groups, all_valid = test_depth_grouping()

        print("\n" + "=" * 80)
        if all_valid:
            print("🎉 TEST RÉUSSI !")
        else:
            print("⚠️  TEST ÉCHOUÉ - Vérifier le prompt du LLM")
        print("=" * 80)

    except Exception as e:
        print("\n\n" + "=" * 80)
        print("❌ ERREUR:")
        print("=" * 80)
        import traceback
        traceback.print_exc()
