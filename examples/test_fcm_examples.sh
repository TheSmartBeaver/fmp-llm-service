#!/bin/bash
#
# Exemples de commandes pour tester les notifications FCM
#
# IMPORTANT: Remplacez "VOTRE_AUTH_UID" par votre véritable auth_uid Firebase
#

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Exemples de Test FCM ===${NC}\n"

# Configuration
BASE_URL="http://localhost:8003"
AUTH_UID="2EC4k3nW3AXAJeMAuYV5R79bB2x2"  # ⚠️ CHANGEZ CECI !

if [ "$AUTH_UID" = "VOTRE_AUTH_UID" ]; then
    echo -e "${RED}❌ ERREUR: Veuillez modifier AUTH_UID dans ce script avec votre véritable auth_uid${NC}"
    echo -e "${YELLOW}   Éditez ce fichier: examples/test_fcm_examples.sh${NC}"
    echo -e "${YELLOW}   Ligne 13: AUTH_UID=\"votre_vrai_auth_uid\"${NC}\n"
    exit 1
fi

echo -e "${GREEN}📱 Auth UID configuré: ${AUTH_UID}${NC}\n"

# ============================================================================
# EXEMPLE 1: Notification simple avec valeurs par défaut
# ============================================================================
echo -e "${BLUE}📤 Exemple 1: Notification simple (valeurs par défaut)${NC}"
echo "---"
curl -X POST "${BASE_URL}/devices/test-notification" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: ${AUTH_UID}" \
  -d '{}'
echo -e "\n"

sleep 2

# ============================================================================
# EXEMPLE 2: Notification personnalisée
# ============================================================================
echo -e "${BLUE}📤 Exemple 2: Notification personnalisée${NC}"
echo "---"
curl -X POST "${BASE_URL}/devices/test-notification" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: ${AUTH_UID}" \
  -d '{
    "title": "🎉 Supports générés!",
    "body": "Vos supports de cours sont prêts à être consultés"
  }'
echo -e "\n"

sleep 2

# ============================================================================
# EXEMPLE 3: Notification avec données personnalisées
# ============================================================================
echo -e "${BLUE}📤 Exemple 3: Notification avec données pour navigation${NC}"
echo "---"
curl -X POST "${BASE_URL}/devices/test-notification" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: ${AUTH_UID}" \
  -d '{
    "title": "Nouveaux supports disponibles",
    "body": "3 supports de cours ont été générés",
    "data": {
      "action": "navigate",
      "screen": "course_materials",
      "course_id": "12345",
      "supports_count": "3"
    }
  }'
echo -e "\n"

sleep 2

# ============================================================================
# EXEMPLE 4: Notification d'erreur simulée
# ============================================================================
echo -e "${BLUE}📤 Exemple 4: Notification d'erreur${NC}"
echo "---"
curl -X POST "${BASE_URL}/devices/test-notification" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: ${AUTH_UID}" \
  -d '{
    "title": "⚠️ Erreur de génération",
    "body": "Une erreur est survenue lors de la génération des supports",
    "data": {
      "action": "show_error",
      "error_code": "GEN_001"
    }
  }'
echo -e "\n"

sleep 2

# ============================================================================
# EXEMPLE 5: Vérifier les appareils enregistrés
# ============================================================================
echo -e "${BLUE}📱 Exemple 5: Liste de vos appareils enregistrés${NC}"
echo "---"
curl -X GET "${BASE_URL}/devices/" \
  -H "X-Auth-Uid: ${AUTH_UID}"
echo -e "\n"

echo -e "${GREEN}✅ Tests terminés!${NC}"
echo -e "${YELLOW}💡 Astuce: Vérifiez votre application Flutter pour voir les notifications${NC}"
