"""
Test du correcteur avec un niveau section/container intermédiaire.
"""

from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections
from app.chains.correctors.implementations import ListeExemplesHoistCorrector
import json


def test_liste_exemples_with_section():
    """Test avec section/container contenant title."""
    print("\n=== Test: Remontée avec section/container ===\n")

    structure = {
        "supports": [
            {
                "support": {
                    "template_name": None,
                    "version": "1.0.0",
                    "support": {
                        "template_name": "section/container",
                        "title": "Exemples supplémentaires",
                        "content": {
                            "template_name": "temporal/present/container",
                            "items": [
                                {
                                    "template_name": "temporal/present/item",
                                    "start": {
                                        "template_name": "text/liste_exemples",
                                        "items": [
                                            {
                                                "template_name": "text/contexte",
                                                "text": "<li><strong>Contexte :</strong> {-{examples_in_context[0]->examples[2]->context_fr}-}</li>"
                                            },
                                            {
                                                "template_name": "text/sous_titre",
                                                "text": "<li><strong>Phrase espagnole :</strong> {-{examples_in_context[0]->examples[2]->sentence_es}-}</li>"
                                            },
                                            {
                                                "template_name": "text/annotation",
                                                "text": "<li><strong>Note pédagogique :</strong> {-{examples_in_context[0]->examples[2]->note}-}</li>"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }

    print("Structure AVANT correction:")
    print(json.dumps(structure, indent=2, ensure_ascii=False))

    # Créer le registry avec le correcteur
    registry = CorrectorRegistry()
    registry.register(ListeExemplesHoistCorrector())

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

    # Naviguer vers section/container
    section = corrected["supports"][0]["support"]["support"]

    # Vérifier que section/container est toujours là
    assert section.get("template_name") == "section/container", \
        "section/container doit être préservé"
    print(f"  ✓ section/container préservé")

    # Vérifier que title est préservé
    assert section.get("title") == "Exemples supplémentaires", \
        "Le title doit être préservé"
    print(f"  ✓ title préservé: {section['title']}")

    # Vérifier que content est maintenant text/liste_exemples
    content = section.get("content")
    assert isinstance(content, dict), "content doit être un dict"
    assert content.get("template_name") == "text/liste_exemples", \
        "content doit être text/liste_exemples"
    print(f"  ✓ content est text/liste_exemples")

    # Vérifier que les items sont préservés
    items = content.get("items")
    assert len(items) == 3, "Il doit y avoir 3 items"
    print(f"  ✓ {len(items)} items préservés")

    # Vérifier les template_names des items
    expected_items = ["text/contexte", "text/sous_titre", "text/annotation"]
    actual_items = [item.get("template_name") for item in items]
    assert actual_items == expected_items, \
        f"Items attendus: {expected_items}, obtenus: {actual_items}"
    print(f"  ✓ Items corrects: {actual_items}")

    # Vérifier qu'il n'y a plus de temporal containers
    json_str = json.dumps(corrected, ensure_ascii=False)
    assert "temporal/present/container" not in json_str, \
        "temporal/present/container ne doit plus être présent"
    assert "temporal/present/item" not in json_str, \
        "temporal/present/item ne doit plus être présent"
    print(f"  ✓ Containers temporels supprimés")

    # Vérifier que version est préservé
    assert corrected["supports"][0]["support"]["version"] == "1.0.0", \
        "version doit être préservé"
    print(f"  ✓ version préservé")

    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS SONT PASSÉS !")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_liste_exemples_with_section()
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
