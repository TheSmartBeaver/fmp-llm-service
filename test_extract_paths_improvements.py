"""
Test pour vérifier que _extract_all_json_paths génère correctement:
1. Utilise toujours -> entre propriétés
2. Ajoute [x] pour les tableaux de primitives
3. Utilise -> après les indices de tableau
"""
import json
from app.chains.template_structure_generator import TemplateStructureGenerator


# JSON de test avec différents cas
test_json = {
    "course": "Espagnol",
    "summary": {
        "title": "Conjugaison",
        "explanation": "Explication longue..."
    },
    "learningStrategies": {
        "principles": "Un principe simple (string, pas tableau)",
        "concreteTips": [
            "Conseil 1",
            "Conseil 2",
            "Conseil 3"
        ],
        "pitfallsToAvoid": "Éviter les pièges..."
    },
    "glossary": [
        {
            "term": "Infinitif",
            "definition": "Forme nominale"
        },
        {
            "term": "Radical",
            "definition": "Partie du verbe"
        }
    ],
    "themes": [
        {
            "name": "Verbes réguliers",
            "details": [
                "Détail 1",
                "Détail 2"
            ],
            "groups": [
                {
                    "label": "Groupe 1",
                    "exampleSentences": [
                        "Phrase 1",
                        "Phrase 2"
                    ]
                }
            ]
        }
    ]
}


def test_extract_paths_improvements():
    """Tester que _extract_all_json_paths génère les bons chemins."""
    print("=" * 80)
    print("TEST DE _extract_all_json_paths")
    print("=" * 80)

    generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

    # Extraire les chemins
    result = generator._extract_all_json_paths(
        test_json,
        include_indices=False,
        use_variables=True
    )

    # Le résultat peut être une string ou une liste
    if isinstance(result, str):
        paths = [line.strip() for line in result.strip().split('\n') if line.strip()]
    else:
        paths = result

    print(f"\n📊 Nombre de chemins extraits: {len(paths)}")
    print("\n" + "=" * 80)
    print("CHEMINS EXTRAITS")
    print("=" * 80)
    for path in paths:
        print(f"  - {path}")

    # Vérifications
    print("\n" + "=" * 80)
    print("VÉRIFICATIONS")
    print("=" * 80)

    issues = []

    # Vérification 1: -> doit être utilisé entre propriétés
    print("\n1. Vérification: -> entre propriétés")
    for path in paths:
        # Chercher les cas où on a 2 mots consécutifs sans ->
        # Ex: "glossary[x]term" devrait être "glossary[x]->term"
        if "[x]" in path or "[y]" in path or "[z]" in path:
            # Après un indice, il doit y avoir -> si suivi d'une propriété
            import re
            # Chercher pattern [x]mot sans ->
            bad_patterns = re.findall(r'\[[xyz]\]([a-zA-Z])', path)
            if bad_patterns:
                issues.append(f"   ❌ Manque -> après indice: {path}")
                print(f"   ❌ {path} - manque -> après indice")

    if not any("Manque -> après indice" in issue for issue in issues):
        print("   ✅ Tous les chemins utilisent -> après les indices")

    # Vérification 2: Les tableaux de primitives doivent avoir [x]
    print("\n2. Vérification: Tableaux de primitives avec [x]")
    expected_arrays = [
        "learningStrategies->concreteTips[x]",
        "themes[x]->details[y]",
        "themes[x]->groups[y]->exampleSentences[z]"
    ]

    for expected in expected_arrays:
        if expected in paths:
            print(f"   ✅ {expected}")
        else:
            issues.append(f"   ❌ Manquant: {expected}")
            print(f"   ❌ Manquant: {expected}")

    # Vérification 3: Les strings simples ne doivent PAS avoir [x]
    print("\n3. Vérification: Strings simples SANS [x]")
    simple_strings = [
        "learningStrategies->principles",
        "learningStrategies->pitfallsToAvoid"
    ]

    for expected in simple_strings:
        if expected in paths:
            print(f"   ✅ {expected} (sans [x], correct)")
        else:
            # Vérifier si on a incorrectement ajouté [x]
            with_x = f"{expected}[x]"
            if with_x in paths:
                issues.append(f"   ❌ {with_x} ne devrait pas avoir [x]")
                print(f"   ❌ {with_x} ne devrait PAS avoir [x] (c'est une string, pas un tableau)")

    # Vérification 4: -> entre toutes les propriétés imbriquées
    print("\n4. Vérification: -> entre propriétés imbriquées")
    expected_with_arrow = [
        "summary->title",
        "summary->explanation",
        "glossary[x]->term",
        "glossary[x]->definition",
        "themes[x]->name",
        "themes[x]->groups[y]->label"
    ]

    for expected in expected_with_arrow:
        if expected in paths:
            print(f"   ✅ {expected}")
        else:
            issues.append(f"   ❌ Manquant ou mal formé: {expected}")
            print(f"   ❌ Manquant: {expected}")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    if not issues:
        print("\n✅ TOUS LES TESTS PASSENT!")
        print("   - -> est utilisé entre toutes les propriétés")
        print("   - [x] est ajouté pour les tableaux de primitives")
        print("   - [x] n'est PAS ajouté pour les strings simples")
    else:
        print(f"\n❌ {len(issues)} PROBLÈME(S) DÉTECTÉ(S):")
        for issue in issues:
            print(issue)

    # Sauvegarder
    output = {
        "paths_count": len(paths),
        "paths": paths,
        "issues": issues,
        "test_passed": len(issues) == 0
    }

    with open("test_extract_paths_improvements_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ Résultat sauvegardé dans: test_extract_paths_improvements_output.json")
    print("=" * 80)


if __name__ == "__main__":
    test_extract_paths_improvements()
