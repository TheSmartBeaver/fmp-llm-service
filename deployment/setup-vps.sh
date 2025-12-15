#!/bin/bash

# Script de configuration initiale du VPS pour le déploiement automatique
# Usage: ./setup-vps.sh

set -e

echo "========================================="
echo "Configuration du VPS pour FMP LLM Service"
echo "========================================="

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables par défaut (modifiables)
DEPLOY_PATH=${DEPLOY_PATH:-"/opt/fmp-llm-service"}
APP_USER=${APP_USER:-"root"}

echo -e "${YELLOW}Chemin de déploiement: ${DEPLOY_PATH}${NC}"
echo -e "${YELLOW}Utilisateur: ${APP_USER}${NC}"

# Mise à jour du système
echo -e "\n${GREEN}[1/6] Mise à jour du système...${NC}"
apt-get update
apt-get upgrade -y

# Installation de Docker
echo -e "\n${GREEN}[2/6] Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}Docker installé avec succès${NC}"
else
    echo -e "${YELLOW}Docker est déjà installé${NC}"
fi

# Installation de Docker Compose
echo -e "\n${GREEN}[3/6] Installation de Docker Compose...${NC}"
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo -e "${GREEN}Docker Compose installé avec succès${NC}"
else
    echo -e "${YELLOW}Docker Compose est déjà installé${NC}"
fi

# Vérification des versions
echo -e "\n${GREEN}Versions installées:${NC}"
docker --version
docker compose version

# Création du répertoire de déploiement
echo -e "\n${GREEN}[4/6] Création du répertoire de déploiement...${NC}"
mkdir -p "${DEPLOY_PATH}"
mkdir -p "${DEPLOY_PATH}/dl_models"
echo -e "${GREEN}Répertoire créé: ${DEPLOY_PATH}${NC}"

# Configuration du pare-feu (optionnel)
echo -e "\n${GREEN}[5/6] Configuration du pare-feu...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 8003/tcp
    echo -e "${GREEN}Port 8003 autorisé${NC}"
else
    echo -e "${YELLOW}UFW n'est pas installé, ignoré${NC}"
fi

# Affichage de la clé publique SSH pour GitHub Actions
echo -e "\n${GREEN}[6/6] Configuration SSH...${NC}"
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${YELLOW}Aucune clé SSH trouvée. Génération...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Configuration terminée avec succès!${NC}"
echo -e "${GREEN}=========================================${NC}"

echo -e "\n${YELLOW}Prochaines étapes:${NC}"
echo -e "1. Ajoutez ces secrets dans GitHub (Settings > Secrets and variables > Actions):"
echo -e "   - VPS_SSH_KEY: Votre clé privée SSH (contenu de ~/.ssh/id_rsa)"
echo -e "   - VPS_HOST: L'adresse IP de ce VPS"
echo -e "   - VPS_USER: ${APP_USER}"
echo -e "   - DEPLOY_PATH: ${DEPLOY_PATH}"
echo -e "   - ENV_FILE: Contenu de votre fichier .env"
echo -e "\n2. Créez le fichier .env dans ${DEPLOY_PATH}/ avec vos variables d'environnement"
echo -e "\n3. Push votre code sur la branche main pour déclencher le déploiement"

echo -e "\n${YELLOW}Clé publique SSH (à ajouter aux authorized_keys si nécessaire):${NC}"
cat ~/.ssh/id_rsa.pub
