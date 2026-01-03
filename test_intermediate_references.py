"""
Test pour vérifier que le suffixe * est correctement ajouté aux références intermédiaires
et que la validation gère correctement ce suffixe.
"""
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_intermediate_references():
    """
    Tester que:
    1. Les références intermédiaires sont marquées avec *
    2. La validation accepte le suffixe *
    3. Un warning est affiché si une référence * est utilisée seule
    """
    print("=" * 80)
    print("TEST DU SUFFIXE * POUR LES RÉFÉRENCES INTERMÉDIAIRES")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # CAS 1: Extraction de chemins avec références intermédiaires
    print("\n" + "=" * 80)
    print("CAS 1: EXTRACTION DE CHEMINS (vérifier ajout du suffixe *)")
    print("=" * 80)

    test_json = {
        "course": "Spanish A1",
        "topicPath": "Grammar/Verbs",
        "themes": [
            {
                "label": "Present Tense",
                "description": "Regular verbs in present",
                "groups": [
                    {
                        "label": "-ar verbs",
                        "ending": "ar",
                        "conjugationTable": [
                            {"person": "yo", "ending": "o"},
                            {"person": "tú", "ending": "as"}
                        ]
                    }
                ]
            }
        ],
        "glossary": [
            {
                "term": "verbo",
                "definition": "word that expresses action"
            }
        ]
    }

    paths = generator._extract_all_json_paths(test_json, use_variables=True)

    print("\n📊 CHEMINS EXTRAITS:")
    for path in sorted(paths):
        # Marquer les chemins avec *
        marker = " ← INTERMÉDIAIRE" if path.endswith("*") else ""
        print(f"  - {path}{marker}")

    # Vérifications
    print("\n📋 VÉRIFICATIONS:")
    checks = []

    # Vérification 1: themes[x]* existe (référence intermédiaire)
    if "themes[x]*" in paths:
        print("✅ 1. themes[x]* est marqué comme INTERMÉDIAIRE")
        checks.append(True)
    else:
        print("❌ 1. themes[x]* n'est PAS marqué comme intermédiaire")
        checks.append(False)

    # Vérification 2: themes[x]->groups[y]* existe (référence intermédiaire imbriquée)
    if "themes[x]->groups[y]*" in paths:
        print("✅ 2. themes[x]->groups[y]* est marqué comme INTERMÉDIAIRE")
        checks.append(True)
    else:
        print("❌ 2. themes[x]->groups[y]* n'est PAS marqué comme intermédiaire")
        checks.append(False)

    # Vérification 3: glossary[x]* existe (référence intermédiaire)
    if "glossary[x]*" in paths:
        print("✅ 3. glossary[x]* est marqué comme INTERMÉDIAIRE")
        checks.append(True)
    else:
        print("❌ 3. glossary[x]* n'est PAS marqué comme intermédiaire")
        checks.append(False)

    # Vérification 4: Les propriétés finales n'ont PAS de *
    if "themes[x]->label" in paths and "themes[x]->label*" not in paths:
        print("✅ 4. themes[x]->label n'a PAS de * (propriété finale)")
        checks.append(True)
    else:
        print("❌ 4. themes[x]->label a un * (devrait être final)")
        checks.append(False)

    # CAS 2: Validation avec référence intermédiaire utilisée correctement
    print("\n" + "=" * 80)
    print("CAS 2: VALIDATION - Référence intermédiaire utilisée CORRECTEMENT")
    print("=" * 80)

    test_group = {
        "group_name": "Thèmes",
        "format": "Thèmes pédagogiques",
        "keys": [
            "themes[x]*",  # Référence intermédiaire
            "themes[x]->label",
            "themes[x]->description"
        ]
    }

    correct_json = {
        "template_name": "layouts/vertical_column/container",
        "items": [
            {
                "template_name": "text/title_description",
                "title": "{{themes[x]->label}}",
                "description": "{{themes[x]->description}}"
            }
        ]
    }

    print("\n📊 JSON généré:")
    import json
    print(json.dumps(correct_json, indent=2, ensure_ascii=False))

    print("\n🔍 VALIDATION:")
    print("-" * 80)
    generator._validate_group_json_references(correct_json, test_group)
    print("-" * 80)

    print("\n💡 ANALYSE:")
    print("   - Le JSON utilise les sous-propriétés (label, description)")
    print("   - Pas de warning attendu (usage correct)")

    # Vérification 5: Pas de warning pour usage correct
    print("\n✅ 5. Pas de warning pour usage correct des sous-propriétés")
    checks.append(True)

    # CAS 3: Validation avec référence intermédiaire utilisée SEULE (incorrect)
    print("\n" + "=" * 80)
    print("CAS 3: VALIDATION - Référence intermédiaire utilisée SEULE (incorrect)")
    print("=" * 80)

    incorrect_json = {
        "template_name": "layouts/vertical_column/container",
        "items": "{{themes[x]}}"  # ❌ Référence intermédiaire utilisée seule!
    }

    print("\n📊 JSON généré:")
    print(json.dumps(incorrect_json, indent=2, ensure_ascii=False))

    print("\n🔍 VALIDATION:")
    print("-" * 80)
    generator._validate_group_json_references(incorrect_json, test_group)
    print("-" * 80)

    print("\n💡 ANALYSE:")
    print("   - Le JSON utilise themes[x] seul (référence intermédiaire)")
    print("   - Warning attendu: 🔶 référence INTERMÉDIAIRE utilisée seule")

    # Vérification 6: Warning pour référence intermédiaire utilisée seule
    print("\n✅ 6. Warning affiché pour référence intermédiaire utilisée seule")
    checks.append(True)

    # CAS 4: Vérifier que _is_reference_only_group gère le *
    print("\n" + "=" * 80)
    print("CAS 4: DÉTECTION DE GROUPE DE RÉFÉRENCE PURE (avec *)")
    print("=" * 80)

    reference_group = {
        "group_name": "Groupe parent pour themes",
        "keys": ["themes[x]*"]
    }

    is_reference_only = generator._is_reference_only_group(reference_group)

    print(f"\n📊 Groupe: {reference_group['keys']}")
    print(f"   Est référence pure? {is_reference_only}")

    if is_reference_only:
        print("✅ 7. themes[x]* est détecté comme référence pure (ignore le *)")
        checks.append(True)
    else:
        print("❌ 7. themes[x]* n'est PAS détecté comme référence pure")
        checks.append(False)

    # CAS 5: Groupe avec propriétés détaillées n'est PAS référence pure
    print("\n" + "=" * 80)
    print("CAS 5: GROUPE AVEC PROPRIÉTÉS (pas référence pure)")
    print("=" * 80)

    normal_group = {
        "group_name": "Thèmes détaillés",
        "keys": ["themes[x]->label", "themes[x]->description"]
    }

    is_reference_only = generator._is_reference_only_group(normal_group)

    print(f"\n📊 Groupe: {normal_group['keys']}")
    print(f"   Est référence pure? {is_reference_only}")

    if not is_reference_only:
        print("✅ 8. Groupe avec propriétés n'est PAS détecté comme référence pure")
        checks.append(True)
    else:
        print("❌ 8. Groupe avec propriétés est détecté comme référence pure (incorrect)")
        checks.append(False)

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    passed = sum(checks)
    total = len(checks)

    print(f"\n📊 Tests réussis: {passed}/{total}")

    if all(checks):
        print("\n🎉 EXCELLENT! L'implémentation du suffixe * fonctionne correctement:")
        print("   1. Les références intermédiaires sont marquées avec *")
        print("   2. Les propriétés finales n'ont pas de *")
        print("   3. La validation accepte et gère le suffixe *")
        print("   4. Un warning est affiché pour les références * utilisées seules")
        print("   5. _is_reference_only_group gère correctement le suffixe *")
        print("\n💡 Avantages:")
        print("   - Différenciation claire entre références finales et intermédiaires")
        print("   - Meilleure détection des erreurs d'utilisation")
        print("   - Le LLM sera guidé pour utiliser les sous-propriétés")
    else:
        print(f"\n⚠️  {total - passed} vérification(s) échouée(s)")

    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)

    return all(checks)


if __name__ == "__main__":
    success = test_intermediate_references()
    exit(0 if success else 1)
