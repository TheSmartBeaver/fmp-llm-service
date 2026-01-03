"""
Test pour vérifier que le prompt contient des instructions spéciales
pour les groupes de référence pure.
"""
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_reference_group_prompt():
    """
    Tester que le prompt contient des instructions spéciales pour les groupes de référence pure.
    """
    print("=" * 80)
    print("TEST DU PROMPT POUR GROUPES DE RÉFÉRENCE PURE")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Templates de test (simplifiés)
    test_templates = [
        {
            "template_name": "layouts/vertical_column/container",
            "description": "Container vertical",
            "fields_usage": {
                "items": "Liste d'éléments"
            }
        }
    ]

    # CAS 1: Groupe de référence pure
    print("\n" + "=" * 80)
    print("CAS 1: GROUPE DE RÉFÉRENCE PURE (glossary[x])")
    print("=" * 80)

    reference_group = {
        "group_name": "Groupe parent pour glossary",
        "format": "Glossaire",
        "keys": ["glossary[x]"],
        "is_reference_only": True
    }

    prompt, params = generator._build_json_generation_prompt(reference_group, test_templates)
    messages = prompt.format_messages(**params)
    user_message = messages[1].content

    print("\n📊 PROMPT UTILISATEUR:")
    print("-" * 80)
    print(user_message)
    print("-" * 80)

    # Vérifications
    print("\n📋 VÉRIFICATIONS:")
    checks = []

    # Vérification 1: Instructions spéciales présentes
    if "ATTENTION SPÉCIALE" in user_message:
        print("✅ 1. Instructions spéciales présentes")
        checks.append(True)
    else:
        print("❌ 1. Instructions spéciales manquantes")
        checks.append(False)

    # Vérification 2: Interdiction d'inventer des propriétés
    if "N'invente PAS de propriétés" in user_message:
        print("✅ 2. Interdiction explicite d'inventer des propriétés")
        checks.append(True)
    else:
        print("❌ 2. Pas d'interdiction explicite")
        checks.append(False)

    # Vérification 3: Exemple CORRECT fourni
    if "Exemple CORRECT" in user_message and "{{glossary[x]}}" in user_message:
        print("✅ 3. Exemple CORRECT fourni (utilise la référence telle quelle)")
        checks.append(True)
    else:
        print("❌ 3. Pas d'exemple CORRECT")
        checks.append(False)

    # Vérification 4: Exemple INCORRECT fourni
    if "Exemple INCORRECT" in user_message and "{{glossary[x]->term}}" in user_message:
        print("✅ 4. Exemple INCORRECT fourni (montre ce qu'il ne faut PAS faire)")
        checks.append(True)
    else:
        print("❌ 4. Pas d'exemple INCORRECT")
        checks.append(False)

    # CAS 2: Groupe normal (avec propriétés)
    print("\n" + "=" * 80)
    print("CAS 2: GROUPE NORMAL (avec propriétés détaillées)")
    print("=" * 80)

    normal_group = {
        "group_name": "Glossaire",
        "format": "Termes du glossaire",
        "keys": ["glossary[x]->term", "glossary[x]->definition"],
        "is_reference_only": False
    }

    prompt2, params2 = generator._build_json_generation_prompt(normal_group, test_templates)
    messages2 = prompt2.format_messages(**params2)
    user_message2 = messages2[1].content

    print("\n📊 PROMPT UTILISATEUR:")
    print("-" * 80)
    print(user_message2)
    print("-" * 80)

    print("\n📋 VÉRIFICATIONS:")

    # Vérification 5: Pas d'instructions spéciales pour groupe normal
    if "ATTENTION SPÉCIALE" not in user_message2:
        print("✅ 5. Pas d'instructions spéciales pour groupe normal (correct)")
        checks.append(True)
    else:
        print("❌ 5. Instructions spéciales présentes alors que le groupe n'est pas de référence pure")
        checks.append(False)

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    passed = sum(checks)
    total = len(checks)

    print(f"\n📊 Tests réussis: {passed}/{total}")

    if all(checks):
        print("\n✅ EXCELLENT! Le prompt est correctement configuré:")
        print("   1. Instructions spéciales pour groupes de référence pure")
        print("   2. Interdiction explicite d'inventer des propriétés")
        print("   3. Exemples CORRECT et INCORRECT fournis")
        print("   4. Pas d'instructions spéciales pour groupes normaux")
        print("\n💡 Cela devrait réduire considérablement les hallucinations du type:")
        print("   ❌ {{glossary[x]->term}} (inventé)")
        print("   ✅ {{glossary[x]}} (correct)")
    else:
        print(f"\n⚠️  {total - passed} vérification(s) échouée(s)")

    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)

    return all(checks)


if __name__ == "__main__":
    success = test_reference_group_prompt()
    exit(0 if success else 1)
