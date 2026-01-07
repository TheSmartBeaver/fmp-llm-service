"""
Test pour le correcteur de suppression de blocs dupliqués.
"""

from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections
from app.chains.correctors.implementations import DuplicateBlockRemoverCorrector
import json


def test_duplicate_block_remover():
    """Test de suppression de blocs dupliqués."""
    print("\n=== Test: Suppression de blocs dupliqués ===\n")

    # Structure JSON avec doublons (exemple de l'utilisateur)
    structure = {
        "supports": [
            {
                "support": {
                    "template_name": None,
                    "version": "1.0.0",
                    "support": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/sous_titre",
                                "text": "Parcours guidé des étapes principales de la conjugaison espagnole"
                            },
                            {
                                "template_name": "temporal/timeline_vertical/container",
                                "items": [
                                    {
                                        "template_name": "procedural/etape_numerotee",
                                        "number": "{-{learningPath[0]->stage}-}",
                                        "content": "{-{learningPath[0]->content}-}"
                                    }
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "support": {
                    "template_name": None,
                    "version": "1.0.0",
                    "support": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/sous_titre",
                                "text": "Parcours guidé des étapes principales de la conjugaison espagnole"
                            },
                            {
                                "template_name": "temporal/timeline_vertical/container",
                                "items": [
                                    {
                                        "template_name": "procedural/etape_numerotee",
                                        "number": "{-{learningPath[1]->stage}-}",
                                        "content": "{-{learningPath[1]->content}-}"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        ]
    }

    print("Structure AVANT correction:")
    print(json.dumps(structure, indent=2, ensure_ascii=False))

    # Créer le registry avec le correcteur
    registry = CorrectorRegistry()
    registry.register(DuplicateBlockRemoverCorrector())

    # Appliquer les corrections
    corrected, stats = processSeriesOfCorrections(structure, registry)

    print("\n" + "=" * 60)
    print("Structure APRÈS correction:")
    print(json.dumps(corrected, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("Statistiques:")
    print(f"  Correcteurs applicables: {stats['applicable_correctors_count']}")
    print(f"  Itérations effectuées: {stats['total_iterations']}")
    print(f"  Corrections par correcteur: {stats['corrections_by_corrector']}")
    print(f"  Erreurs: {stats.get('errors', [])}")

    # Vérifications
    print("\n" + "=" * 60)
    print("Vérifications:")

    # Vérifier que le premier support a bien le text/sous_titre
    first_support_items = corrected["supports"][0]["support"]["support"]["items"]
    has_sous_titre_first = any(
        item.get("template_name") == "text/sous_titre"
        for item in first_support_items
    )
    print(f"  ✓ Premier support a text/sous_titre: {has_sous_titre_first}")
    assert has_sous_titre_first, "Le premier support devrait avoir text/sous_titre"

    # Vérifier que le deuxième support n'a PAS le text/sous_titre (dupliqué supprimé)
    second_support_items = corrected["supports"][1]["support"]["support"]["items"]
    has_sous_titre_second = any(
        item.get("template_name") == "text/sous_titre"
        for item in second_support_items
    )
    print(f"  ✓ Deuxième support n'a PAS text/sous_titre: {not has_sous_titre_second}")
    assert not has_sous_titre_second, "Le deuxième support ne devrait PAS avoir text/sous_titre (dupliqué)"

    # Vérifier que les deux supports ont toujours leur timeline
    has_timeline_first = any(
        item.get("template_name") == "temporal/timeline_vertical/container"
        for item in first_support_items
    )
    has_timeline_second = any(
        item.get("template_name") == "temporal/timeline_vertical/container"
        for item in second_support_items
    )
    print(f"  ✓ Premier support a timeline: {has_timeline_first}")
    print(f"  ✓ Deuxième support a timeline: {has_timeline_second}")
    assert has_timeline_first, "Le premier support devrait avoir sa timeline"
    assert has_timeline_second, "Le deuxième support devrait avoir sa timeline"

    # Vérifier que le nombre d'items dans le deuxième support est réduit de 1
    print(f"  ✓ Premier support a {len(first_support_items)} items")
    print(f"  ✓ Deuxième support a {len(second_support_items)} items")
    assert len(first_support_items) == 2, "Le premier support devrait avoir 2 items"
    assert len(second_support_items) == 1, "Le deuxième support devrait avoir 1 item (doublon supprimé)"

    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS SONT PASSÉS !")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_duplicate_block_remover()
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
