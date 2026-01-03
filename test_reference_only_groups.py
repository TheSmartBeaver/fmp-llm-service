"""
Test pour vérifier que _is_reference_only_group détecte correctement
les groupes de référence pure.
"""
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_reference_only_groups():
    """
    Tester la détection des groupes de référence pure.
    """
    print("=" * 80)
    print("TEST DE DÉTECTION DES GROUPES DE RÉFÉRENCE PURE")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    test_cases = [
        # CAS 1: Groupe de référence pure (glossary[x])
        {
            "name": "Groupe de référence pure - glossary[x]",
            "group": {
                "group_name": "Groupe parent pour glossary",
                "keys": ["glossary[x]"],
                "format": "Glossaire"
            },
            "expected": True,
            "reason": "Contient seulement 'glossary[x]' sans propriétés"
        },

        # CAS 2: Groupe de référence pure (themes[x])
        {
            "name": "Groupe de référence pure - themes[x]",
            "group": {
                "group_name": "Groupe parent pour themes",
                "keys": ["themes[x]"],
                "format": "Thèmes"
            },
            "expected": True,
            "reason": "Contient seulement 'themes[x]' sans propriétés"
        },

        # CAS 3: Groupe avec propriétés détaillées
        {
            "name": "Groupe avec propriétés - glossary[x]->term, definition",
            "group": {
                "group_name": "Glossaire",
                "keys": ["glossary[x]->term", "glossary[x]->definition"],
                "format": "Termes du glossaire"
            },
            "expected": False,
            "reason": "Contient des propriétés détaillées après ->"
        },

        # CAS 4: Groupe avec propriétés simples (sans variables)
        {
            "name": "Groupe avec propriétés simples - course, topicPath",
            "group": {
                "group_name": "Métadonnées",
                "keys": ["course", "topicPath"],
                "format": "Informations de cours"
            },
            "expected": False,
            "reason": "Propriétés simples sans variables"
        },

        # CAS 5: Groupe de référence pure avec plusieurs variables (themes[x]->examples[y])
        {
            "name": "Groupe de référence pure - themes[x]->examples[y]",
            "group": {
                "group_name": "Groupe parent pour examples",
                "keys": ["themes[x]->examples[y]"],
                "format": "Exemples"
            },
            "expected": True,
            "reason": "Référence pure se terminant par [y] sans propriétés après"
        },

        # CAS 6: Groupe avec propriétés imbriquées
        {
            "name": "Groupe avec propriétés - themes[x]->examples[y]->label, infinitive",
            "group": {
                "group_name": "Exemples détaillés",
                "keys": [
                    "themes[x]->examples[y]->label",
                    "themes[x]->examples[y]->infinitive",
                    "themes[x]->examples[y]->explanation"
                ],
                "format": "Exemples avec détails"
            },
            "expected": False,
            "reason": "Contient des propriétés après la dernière variable"
        },

        # CAS 7: Groupe de référence pure - themes[x]->examples[y]->conjugation[z]
        {
            "name": "Groupe de référence pure - conjugation[z]",
            "group": {
                "group_name": "Groupe parent pour conjugation",
                "keys": ["themes[x]->examples[y]->conjugation[z]"],
                "format": "Conjugaison"
            },
            "expected": True,
            "reason": "Référence pure se terminant par [z] sans propriétés après"
        },

        # CAS 8: Groupe mixte (devrait être False)
        {
            "name": "Groupe mixte - référence + propriétés",
            "group": {
                "group_name": "Groupe mixte",
                "keys": ["glossary[x]", "glossary[x]->term"],
                "format": "Mixte"
            },
            "expected": False,
            "reason": "Contient à la fois une référence et une propriété"
        },

        # CAS 9: Groupe vide (devrait être False)
        {
            "name": "Groupe vide",
            "group": {
                "group_name": "Groupe vide",
                "keys": [],
                "format": "Vide"
            },
            "expected": False,
            "reason": "Aucune clé"
        },
    ]

    # Exécuter les tests
    print("\n" + "=" * 80)
    print("RÉSULTATS DES TESTS")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        result = generator._is_reference_only_group(test_case["group"])
        expected = test_case["expected"]

        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"\n{i}. {test_case['name']}")
        print(f"   Clés: {test_case['group']['keys']}")
        print(f"   Résultat: {result} (attendu: {expected})")
        print(f"   Raison: {test_case['reason']}")
        print(f"   {status}")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    total = len(test_cases)
    print(f"\n📊 Tests exécutés: {total}")
    print(f"✅ Tests réussis: {passed}")
    print(f"❌ Tests échoués: {failed}")

    if failed == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("\n✅ La détection des groupes de référence pure fonctionne correctement:")
        print("   - Détecte les groupes avec seulement des références (glossary[x])")
        print("   - Ne traite pas comme références les groupes avec propriétés détaillées")
        print("   - Gère correctement les références multi-niveaux (themes[x]->examples[y])")
    else:
        print(f"\n⚠️  {failed} test(s) échoué(s)")

    # Sauvegarder
    import json
    output = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "test_cases": [
            {
                "name": tc["name"],
                "keys": tc["group"]["keys"],
                "result": generator._is_reference_only_group(tc["group"]),
                "expected": tc["expected"],
                "reason": tc["reason"]
            }
            for tc in test_cases
        ]
    }

    with open("test_reference_only_groups_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_reference_only_groups_output.json")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_reference_only_groups()
    exit(0 if success else 1)
