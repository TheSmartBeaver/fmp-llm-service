"""
Test pour démontrer le nouveau format de validation avec clés fictives ET manquantes.
"""
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_auto_fix():
    """
    Tester le nouveau format de validation qui affiche:
    - Clés fictives (inventées)
    - Clés manquantes (devraient être utilisées)
    - Liste complète des clés valides avec indicateurs ✅/⚪
    """
    print("=" * 80)
    print("DÉMONSTRATION DU NOUVEAU FORMAT DE VALIDATION")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Groupe de test
    test_group = {
        "format": "Glossaire avec 4 propriétés",
        "keys": [
            "glossary[x]->term",
            "glossary[x]->definition",
            "glossary[x]->example",
            "glossary[x]->notes"
        ]
    }

    # CAS 1: JSON incomplet avec clés fictives et manquantes
    print("\n" + "=" * 80)
    print("CAS 1: JSON INCOMPLET (clés fictives + manquantes)")
    print("=" * 80)

    incomplete_json = {
        "template_name": "text/definition",
        "term": "{{glossary[x]->term}}",
        # definition MANQUANTE
        # example MANQUANTE
        "usage": "{{glossary[x]->usage}}",  # ❌ FICTIF (n'existe pas)
        "pronunciation": "{{glossary[x]->pronunciation}}"  # ❌ FICTIF
    }

    print("\n📊 JSON généré par le LLM:")
    import json
    print(json.dumps(incomplete_json, indent=2, ensure_ascii=False))

    print("\n🔍 VALIDATION:")
    print("-" * 80)
    generator._validate_group_json_references(incomplete_json, test_group)
    print("-" * 80)

    print("\n💡 ANALYSE:")
    print("   - Le LLM a utilisé 1 clé valide: 'term'")
    print("   - Le LLM a inventé 2 clés fictives: 'usage', 'pronunciation'")
    print("   - Le LLM a oublié 3 clés valides: 'definition', 'example', 'notes'")
    print("\n   ✅ Le warning permet de voir:")
    print("      1. Ce qui est FICTIF (à retirer)")
    print("      2. Ce qui MANQUE (à ajouter)")
    print("      3. La liste COMPLÈTE avec indicateurs (utilisé ✅ ou non ⚪)")

    # CAS 2: JSON parfait (toutes les clés utilisées)
    print("\n" + "=" * 80)
    print("CAS 2: JSON PARFAIT (toutes les clés utilisées)")
    print("=" * 80)

    perfect_json = {
        "template_name": "text/definition",
        "term": "{{glossary[x]->term}}",
        "definition": "{{glossary[x]->definition}}",
        "example": "{{glossary[x]->example}}",
        "notes": "{{glossary[x]->notes}}"
    }

    print("\n📊 JSON généré par le LLM:")
    print(json.dumps(perfect_json, indent=2, ensure_ascii=False))

    print("\n🔍 VALIDATION:")
    print("-" * 80)
    generator._validate_group_json_references(perfect_json, test_group)
    print("-" * 80)
    print("\n✅ Aucun warning (JSON parfait)")

    # CAS 3: JSON avec seulement des clés manquantes
    print("\n" + "=" * 80)
    print("CAS 3: JSON PARTIEL (seulement des clés manquantes)")
    print("=" * 80)

    partial_json = {
        "template_name": "text/definition",
        "term": "{{glossary[x]->term}}",
        "definition": "{{glossary[x]->definition}}"
        # example MANQUANTE
        # notes MANQUANTE
    }

    print("\n📊 JSON généré par le LLM:")
    print(json.dumps(partial_json, indent=2, ensure_ascii=False))

    print("\n🔍 VALIDATION:")
    print("-" * 80)
    generator._validate_group_json_references(partial_json, test_group)
    print("-" * 80)

    print("\n💡 ANALYSE:")
    print("   - Aucune clé fictive (pas d'invention)")
    print("   - 2 clés manquantes (le LLM n'a pas utilisé toutes les clés)")
    print("   - Cela peut être normal si certaines clés sont optionnelles")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES AMÉLIORATIONS")
    print("=" * 80)

    print("\n✅ Le nouveau format de validation affiche:")
    print("   1. ❌ Clés FICTIVES: Inventées par le LLM, n'existent pas")
    print("   2. ⚠️  Clés MANQUANTES: Valides mais non utilisées")
    print("   3. 📋 Liste COMPLÈTE: Toutes les clés valides avec indicateurs")
    print("      - ✅ Clé utilisée")
    print("      - ⚪ Clé non utilisée")

    print("\n💡 Avantages:")
    print("   - Vue complète de ce qui va mal")
    print("   - Identification rapide des clés à retirer (fictives)")
    print("   - Identification rapide des clés à ajouter (manquantes)")
    print("   - Facilite le débogage et l'amélioration du prompt")

    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)


if __name__ == "__main__":
    test_auto_fix()
