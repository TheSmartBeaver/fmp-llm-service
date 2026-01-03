"""
Test pour vérifier que le prompt de _build_json_generation_prompt
contient les instructions nécessaires pour éviter les hallucinations du LLM.
"""
from app.chains.template_structure_generator import TemplateStructureGenerator


def test_prompt_improvements():
    """
    Tester que le prompt contient les instructions claires pour:
    1. Utiliser [x], [y], [z] et non [0], [1], [2]
    2. Ne jamais inventer de clés
    3. Utiliser -> entre propriétés
    """
    print("=" * 80)
    print("TEST DES AMÉLIORATIONS DU PROMPT")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Créer un groupe de test
    test_group = {
        "group_name": "Vidéos",
        "format": "Vidéos avec point de démarrage, URL et conseils d'utilisation",
        "keys": [
            "media->videos[x]->label",
            "media->videos[x]->start",
            "media->videos[x]->url",
            "media->videos[x]->usageSuggestion"
        ]
    }

    # Templates de test (simplifiés)
    test_templates = [
        {
            "template_name": "media/video_player",
            "description": "Lecteur vidéo avec titre et URL",
            "fields_usage": {
                "title": "Titre de la vidéo",
                "url": "URL de la vidéo",
                "start_time": "Temps de démarrage"
            }
        }
    ]

    # Construire le prompt
    prompt, params = generator._build_json_generation_prompt(test_group, test_templates)

    # Extraire le texte du prompt système et utilisateur
    messages = prompt.format_messages(**params)
    system_message = messages[0].content
    user_message = messages[1].content

    print("\n📊 PROMPT SYSTÈME")
    print("=" * 80)
    print(system_message)

    print("\n📊 PROMPT UTILISATEUR")
    print("=" * 80)
    print(user_message)

    # Vérifications
    print("\n" + "=" * 80)
    print("VÉRIFICATIONS DES INSTRUCTIONS CRITIQUES")
    print("=" * 80)

    checks = []

    # Vérification 1: Instruction sur les variables [x], [y], [z]
    if "[x]" in system_message and "[y]" in system_message:
        print("✅ 1. Le prompt mentionne les variables [x], [y], [z]")
        checks.append(True)
    else:
        print("❌ 1. Le prompt ne mentionne pas clairement les variables [x], [y], [z]")
        checks.append(False)

    # Vérification 2: Interdiction des indices numériques
    if "[0]" in system_message and "JAMAIS" in system_message:
        print("✅ 2. Le prompt interdit explicitement les indices numériques [0], [1], [2]")
        checks.append(True)
    else:
        print("❌ 2. Le prompt n'interdit pas explicitement les indices numériques")
        checks.append(False)

    # Vérification 3: Instruction sur le séparateur ->
    if "->" in system_message and "séparateur" in system_message.lower():
        print("✅ 3. Le prompt mentionne le séparateur ->")
        checks.append(True)
    else:
        print("❌ 3. Le prompt ne mentionne pas le séparateur ->")
        checks.append(False)

    # Vérification 4: Exemples corrects et incorrects
    if "CORRECT" in system_message and "INCORRECT" in system_message:
        print("✅ 4. Le prompt contient des exemples corrects ET incorrects")
        checks.append(True)
    else:
        print("❌ 4. Le prompt ne montre pas assez clairement les exemples à éviter")
        checks.append(False)

    # Vérification 5: Rappel dans le prompt utilisateur
    if "RAPPEL" in user_message and "[x]" in user_message:
        print("✅ 5. Le prompt utilisateur contient un rappel sur les variables")
        checks.append(True)
    else:
        print("❌ 5. Le prompt utilisateur ne rappelle pas les règles")
        checks.append(False)

    # Vérification 6: Les chemins source sont bien affichés
    if "media->videos[x]->label" in user_message:
        print("✅ 6. Les chemins source avec [x] sont affichés dans le prompt utilisateur")
        checks.append(True)
    else:
        print("❌ 6. Les chemins source ne sont pas bien affichés")
        checks.append(False)

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    passed = sum(checks)
    total = len(checks)

    print(f"\n📊 Tests réussis: {passed}/{total}")

    if all(checks):
        print("\n✅ EXCELLENT! Le prompt contient toutes les instructions nécessaires")
        print("   pour éviter les hallucinations du LLM:")
        print("   - Utilisation obligatoire de [x], [y], [z]")
        print("   - Interdiction des indices numériques [0], [1], [2]")
        print("   - Exemples corrects et incorrects")
        print("   - Rappel dans le prompt utilisateur")
    else:
        print(f"\n⚠️  {total - passed} vérification(s) échouée(s)")
        print("   Le prompt pourrait être amélioré pour réduire les hallucinations")

    # Afficher des extraits clés
    print("\n" + "=" * 80)
    print("EXTRAITS CLÉS DU PROMPT")
    print("=" * 80)

    # Chercher la section sur les variables
    if "RÈGLE CRITIQUE pour les variables" in system_message:
        start = system_message.find("⚠️ RÈGLE CRITIQUE pour les variables")
        end = system_message.find("\n\n", start)
        if end != -1:
            print("\n📌 Section sur les variables:")
            print(system_message[start:end])

    # Chercher les exemples incorrects
    if "Exemples INCORRECTS" in system_message:
        start = system_message.find("Exemples INCORRECTS")
        end = system_message.find("\n\n", start)
        if end != -1:
            print("\n📌 Section exemples incorrects:")
            print(system_message[start:end])

    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)


if __name__ == "__main__":
    test_prompt_improvements()
