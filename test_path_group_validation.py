"""
Test de validation des path_groups
"""
from app.validation.path_group_validator import validate_path_groups


def test_valid_groups():
    """Test avec des groupes valides"""
    print("=== Test 1: Groupes valides ===")

    path_groups = [
        {
            "group_name": "Métadonnées du cours",
            "keys": [
                "metadata->course",
                "metadata->subjectPath",
                "metadata->language"
            ],
            "format": "Informations de base"
        },
        {
            "group_name": "Terminaisons par personne",
            "keys": [
                "conjugationPatterns->endingsByPerson[x]->person",
                "conjugationPatterns->endingsByPerson[x]->ar",
                "conjugationPatterns->endingsByPerson[x]->er"
            ],
            "format": "Tableau comparatif"
        }
    ]

    warnings = validate_path_groups(path_groups)
    if warnings:
        print("❌ Warnings détectés (ne devrait pas arriver):")
        print("\n".join(warnings))
    else:
        print("✅ Aucun warning - groupes valides!")
    print()


def test_mixed_variables():
    """Test avec mélange de clés avec/sans variables"""
    print("=== Test 2: Mélange clés avec/sans variables ===")

    path_groups = [
        {
            "group_name": "Groupe problématique",
            "keys": [
                "metadata->course",  # Sans variable
                "examples->illustrations[x]->sentence"  # Avec variable
            ],
            "format": "Format mixte"
        }
    ]

    warnings = validate_path_groups(path_groups)
    if warnings:
        print("✅ Warning correctement détecté:")
        print("\n".join(warnings))
    else:
        print("❌ Aucun warning détecté (devrait détecter le problème)")
    print()


def test_different_depths():
    """Test avec profondeurs de variables différentes"""
    print("=== Test 3: Profondeurs de variables différentes ===")

    path_groups = [
        {
            "group_name": "Verbes irréguliers",
            "keys": [
                "verbGroups->models[x]->name",  # Profondeur 1
                "verbGroups->models[x]->forms[y]->person"  # Profondeur 2
            ],
            "format": "Liste de verbes"
        }
    ]

    warnings = validate_path_groups(path_groups)
    if warnings:
        print("✅ Warning correctement détecté:")
        print("\n".join(warnings))
    else:
        print("❌ Aucun warning détecté (devrait détecter le problème)")
    print()


def test_different_prefixes():
    """Test avec préfixes différents"""
    print("=== Test 4: Préfixes différents ===")

    path_groups = [
        {
            "group_name": "Groupe multi-préfixes",
            "keys": [
                "comparisons->tableByPerson[x]->person",  # Préfixe: comparisons->tableByPerson[x]
                "examples->illustrations[x]->sentence"    # Préfixe: examples->illustrations[x]
            ],
            "format": "Format multi-sources"
        }
    ]

    warnings = validate_path_groups(path_groups)
    if warnings:
        print("✅ Warning correctement détecté:")
        print("\n".join(warnings))
    else:
        print("❌ Aucun warning détecté (devrait détecter le problème)")
    print()


def test_valid_with_reference():
    """Test avec référence à un groupe imbriqué (valide)"""
    print("=== Test 5: Groupe avec référence imbriquée (valide) ===")

    path_groups = [
        {
            "group_name": "Verbes avec formes imbriquées",
            "keys": [
                "verbGroups->models[x]->name",
                "verbGroups->models[x]->infinitive",
                "verbGroups->models[x]->forms[y]"  # Référence à un autre groupe
            ],
            "format": "Liste de verbes avec formes"
        }
    ]

    warnings = validate_path_groups(path_groups)
    if warnings:
        print("❌ Warnings détectés (ne devrait pas arriver car référence valide):")
        print("\n".join(warnings))
    else:
        print("✅ Aucun warning - groupe avec référence valide!")
    print()


if __name__ == "__main__":
    test_valid_groups()
    test_mixed_variables()
    test_different_depths()
    test_different_prefixes()
    test_valid_with_reference()

    print("=" * 60)
    print("Tests terminés!")
