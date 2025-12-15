#!/bin/bash

# Script de vérification de santé du service FMP LLM
# Usage: ./check-health.sh [HOST] [PORT]

set -e

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
HOST=${1:-"localhost"}
PORT=${2:-"8003"}
BASE_URL="http://${HOST}:${PORT}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Vérification de santé - FMP LLM Service${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "URL: ${BASE_URL}\n"

# Fonction pour afficher un résultat
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Compteur de tests réussis
SUCCESS_COUNT=0
TOTAL_TESTS=0

# 1. Vérifier que Docker est en cours d'exécution
echo -e "${YELLOW}[1/7] Vérification Docker...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if docker ps > /dev/null 2>&1; then
    print_result 0 "Docker est en cours d'exécution"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    print_result 1 "Docker n'est pas accessible"
fi

# 2. Vérifier que le conteneur existe
echo -e "\n${YELLOW}[2/7] Vérification du conteneur...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if docker ps -a | grep -q "fmp-llm-service"; then
    print_result 0 "Conteneur 'fmp-llm-service' trouvé"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

    # Vérifier si le conteneur est en cours d'exécution
    if docker ps | grep -q "fmp-llm-service"; then
        print_result 0 "Conteneur en cours d'exécution"
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        print_result 1 "Conteneur arrêté"
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        echo -e "${RED}Logs du conteneur:${NC}"
        docker logs --tail=20 fmp-llm-service
    fi
else
    print_result 1 "Conteneur 'fmp-llm-service' non trouvé"
fi

# 3. Vérifier le port
echo -e "\n${YELLOW}[3/7] Vérification du port ${PORT}...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if netstat -tuln 2>/dev/null | grep -q ":${PORT} " || ss -tuln 2>/dev/null | grep -q ":${PORT} "; then
    print_result 0 "Port ${PORT} est ouvert"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    print_result 1 "Port ${PORT} n'est pas accessible"
fi

# 4. Vérifier la connectivité HTTP
echo -e "\n${YELLOW}[4/7] Test de connectivité HTTP...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/docs" --connect-timeout 5 || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Endpoint /docs accessible (HTTP ${HTTP_CODE})"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    print_result 1 "Endpoint /docs non accessible (HTTP ${HTTP_CODE})"
fi

# 5. Vérifier l'API de santé (si elle existe)
echo -e "\n${YELLOW}[5/7] Test de l'API...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
API_RESPONSE=$(curl -s "${BASE_URL}/" --connect-timeout 5 || echo "")
if [ -n "$API_RESPONSE" ]; then
    print_result 0 "API répond correctement"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    echo -e "   Réponse: ${API_RESPONSE:0:100}..."
else
    print_result 1 "API ne répond pas"
fi

# 6. Vérifier les logs récents
echo -e "\n${YELLOW}[6/7] Vérification des logs...${NC}"
if docker ps | grep -q "fmp-llm-service"; then
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if docker logs --tail=50 fmp-llm-service 2>&1 | grep -qi "error\|exception\|traceback"; then
        print_result 1 "Erreurs détectées dans les logs"
        echo -e "${RED}Dernières erreurs:${NC}"
        docker logs --tail=50 fmp-llm-service 2>&1 | grep -i "error\|exception" | tail -5
    else
        print_result 0 "Aucune erreur récente dans les logs"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
fi

# 7. Afficher les statistiques du conteneur
echo -e "\n${YELLOW}[7/7] Statistiques du conteneur...${NC}"
if docker ps | grep -q "fmp-llm-service"; then
    docker stats --no-stream fmp-llm-service | tail -n +2
fi

# Résumé
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}Résumé${NC}"
echo -e "${BLUE}=========================================${NC}"

PERCENTAGE=$((SUCCESS_COUNT * 100 / TOTAL_TESTS))

if [ $PERCENTAGE -eq 100 ]; then
    echo -e "${GREEN}✓ Service en parfait état de fonctionnement${NC}"
    echo -e "${GREEN}  Tests réussis: ${SUCCESS_COUNT}/${TOTAL_TESTS} (${PERCENTAGE}%)${NC}"
    exit 0
elif [ $PERCENTAGE -ge 70 ]; then
    echo -e "${YELLOW}⚠ Service partiellement fonctionnel${NC}"
    echo -e "${YELLOW}  Tests réussis: ${SUCCESS_COUNT}/${TOTAL_TESTS} (${PERCENTAGE}%)${NC}"
    exit 1
else
    echo -e "${RED}✗ Service en erreur${NC}"
    echo -e "${RED}  Tests réussis: ${SUCCESS_COUNT}/${TOTAL_TESTS} (${PERCENTAGE}%)${NC}"
    echo -e "\n${YELLOW}Commandes de dépannage:${NC}"
    echo -e "  - Voir les logs: docker compose logs -f"
    echo -e "  - Redémarrer: docker compose restart"
    echo -e "  - Reconstruire: docker compose up -d --build"
    exit 2
fi
