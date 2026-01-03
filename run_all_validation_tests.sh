#!/bin/bash

# Script pour exécuter tous les tests de validation des améliorations

echo "=========================================================================="
echo "EXÉCUTION DE TOUS LES TESTS DE VALIDATION"
echo "=========================================================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

tests_passed=0
tests_failed=0

# Fonction pour exécuter un test
run_test() {
    test_file=$1
    test_name=$2

    echo ""
    echo "=========================================================================="
    echo -e "${BLUE}TEST: $test_name${NC}"
    echo "=========================================================================="

    if .venv/bin/python "$test_file"; then
        echo -e "${GREEN}✅ $test_name: RÉUSSI${NC}"
        ((tests_passed++))
    else
        echo -e "${RED}❌ $test_name: ÉCHOUÉ${NC}"
        ((tests_failed++))
    fi
}

# Exécuter tous les tests
run_test "test_extract_paths_improvements.py" "1. Validation formatage des chemins"
run_test "test_resolve_group_references.py" "2. Validation couverture des clés"
run_test "test_fictive_keys_validation.py" "3. Détection des clés fictives"
run_test "test_prompt_improvements.py" "4. Validation du prompt amélioré"
run_test "test_reference_group_prompt.py" "5. Validation prompt groupes de référence"
run_test "test_auto_fix.py" "6. Format amélioré (fictives + manquantes)"
run_test "test_intermediate_references.py" "7. Suffixe * pour références intermédiaires"
run_test "test_all_improvements.py" "8. Test intégré complet"

# Résumé final
echo ""
echo "=========================================================================="
echo "RÉSUMÉ FINAL"
echo "=========================================================================="

total_tests=$((tests_passed + tests_failed))

echo ""
echo "📊 Tests exécutés: $total_tests"
echo -e "${GREEN}✅ Tests réussis: $tests_passed${NC}"

if [ $tests_failed -gt 0 ]; then
    echo -e "${RED}❌ Tests échoués: $tests_failed${NC}"
    echo ""
    echo "⚠️  Certains tests ont échoué. Veuillez vérifier les erreurs ci-dessus."
    exit 1
else
    echo ""
    echo -e "${GREEN}🎉 TOUS LES TESTS SONT PASSÉS!${NC}"
    echo ""
    echo "✅ Les améliorations suivantes sont validées:"
    echo "   1. Extraction correcte des chemins avec -> et [x]"
    echo "   2. Validation de couverture des clés"
    echo "   3. Détection des clés fictives (3 types)"
    echo "   4. Prompt amélioré avec instructions explicites"
    echo "   5. Instructions spéciales pour groupes de référence pure"
    echo "   6. Format de validation amélioré (fictives + manquantes + liste complète)"
    echo "   7. Suffixe * pour différencier références finales vs intermédiaires"
    echo "   8. Test intégré de toutes les fonctionnalités"
    echo ""
    echo "📚 Documentation:"
    echo "   - IMPROVEMENTS_SUMMARY.md: Documentation détaillée"
    echo "   - FINAL_SUMMARY.md: Résumé exécutif"
    exit 0
fi
