# Guide de déploiement automatique - FMP LLM Service

Ce guide explique comment déployer automatiquement le service FMP LLM sur n'importe quel VPS en utilisant Docker et GitHub Actions.

## Table des matières
- [Prérequis](#prérequis)
- [Configuration initiale du VPS](#configuration-initiale-du-vps)
- [Configuration de GitHub](#configuration-de-github)
- [Premier déploiement](#premier-déploiement)
- [Commandes utiles](#commandes-utiles)
- [Dépannage](#dépannage)

---

## Prérequis

### Sur votre machine locale
- Git
- Accès SSH à votre VPS
- Compte GitHub avec accès au dépôt

### Sur le VPS
- Ubuntu 20.04+ ou Debian 11+
- Accès root ou sudo
- Au minimum 2GB de RAM
- 10GB d'espace disque disponible

---

## Configuration initiale du VPS

### Méthode 1 : Script automatique (recommandé)

1. Connectez-vous à votre VPS :
```bash
ssh root@VOTRE_VPS_IP
```

2. Téléchargez et exécutez le script de configuration :
```bash
curl -fsSL https://raw.githubusercontent.com/VOTRE_USERNAME/fmp-llm-service/main/deployment/setup-vps.sh -o setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh
```

3. Le script affichera votre clé publique SSH à la fin. Gardez-la pour l'étape suivante.

### Méthode 2 : Configuration manuelle

```bash
# 1. Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Installation de Docker Compose
apt-get install -y docker-compose-plugin

# 3. Création du répertoire de déploiement
mkdir -p /opt/fmp-llm-service
mkdir -p /opt/fmp-llm-service/dl_models

# 4. Configuration du pare-feu (optionnel)
ufw allow 8003/tcp

# 5. Génération de la clé SSH (si nécessaire)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
cat ~/.ssh/id_rsa.pub
```

---

## Configuration de GitHub

### 1. Ajouter les secrets GitHub

Allez dans votre dépôt GitHub : **Settings > Secrets and variables > Actions > New repository secret**

Ajoutez les secrets suivants :

| Nom | Valeur | Description |
|-----|--------|-------------|
| `VPS_SSH_KEY` | Contenu de `~/.ssh/id_rsa` | Clé privée SSH pour se connecter au VPS |
| `VPS_HOST` | Ex: `46.202.134.247` | Adresse IP de votre VPS |
| `VPS_USER` | Ex: `root` | Utilisateur SSH sur le VPS |
| `DEPLOY_PATH` | Ex: `/opt/fmp-llm-service` | Chemin de déploiement sur le VPS |
| `ENV_FILE` | Contenu complet de votre `.env` | Variables d'environnement de l'application |

### 2. Récupérer la clé privée SSH

Sur votre VPS, exécutez :
```bash
cat ~/.ssh/id_rsa
```

Copiez **tout le contenu** (y compris les lignes `-----BEGIN` et `-----END`) et collez-le dans le secret `VPS_SSH_KEY`.

### 3. Préparer le fichier ENV_FILE

Votre fichier `.env` devrait contenir :
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Ajoutez toutes vos autres variables d'environnement
```

Copiez le **contenu complet** dans le secret `ENV_FILE`.

---

## Premier déploiement

Une fois les secrets configurés, le déploiement est automatique :

1. Commitez et poussez vos modifications sur la branche `main` :
```bash
git add .
git commit -m "Setup Docker deployment"
git push origin main
```

2. Le workflow GitHub Actions se lance automatiquement. Suivez le déploiement dans **Actions** sur GitHub.

3. Vérifiez le déploiement sur votre VPS :
```bash
ssh root@VOTRE_VPS_IP
cd /opt/fmp-llm-service
docker compose ps
docker compose logs -f
```

4. Testez l'application :
```bash
curl http://VOTRE_VPS_IP:8003/docs
```

---

## Commandes utiles

### Sur le VPS

```bash
# Se connecter au VPS
ssh root@VOTRE_VPS_IP

# Aller dans le répertoire de déploiement
cd /opt/fmp-llm-service

# Voir l'état des conteneurs
docker compose ps

# Voir les logs en temps réel
docker compose logs -f

# Redémarrer le service
docker compose restart

# Arrêter le service
docker compose down

# Démarrer le service
docker compose up -d

# Reconstruire et redémarrer
docker compose up -d --build

# Voir les ressources utilisées
docker stats

# Entrer dans le conteneur
docker compose exec fmp-llm-service bash
```

### Gestion des logs

```bash
# Voir les 100 dernières lignes
docker compose logs --tail=100

# Suivre les logs en temps réel
docker compose logs -f

# Logs d'un service spécifique
docker compose logs fmp-llm-service
```

### Nettoyage

```bash
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les volumes inutilisés
docker volume prune

# Nettoyage complet
docker system prune -a --volumes
```

---

## Déploiement sur un nouveau VPS

Pour déployer sur un nouveau VPS :

1. Exécutez le script de configuration sur le nouveau VPS :
```bash
ssh root@NOUVEAU_VPS_IP
curl -fsSL https://raw.githubusercontent.com/VOTRE_USERNAME/fmp-llm-service/main/deployment/setup-vps.sh -o setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh
```

2. Mettez à jour les secrets GitHub avec la nouvelle IP et clé SSH

3. Poussez un commit pour déclencher le déploiement

C'est tout ! Le service sera déployé automatiquement.

---

## Dépannage

### Le conteneur ne démarre pas

```bash
# Vérifier les logs d'erreur
docker compose logs

# Vérifier que le fichier .env existe
cat /opt/fmp-llm-service/.env

# Reconstruire l'image
docker compose build --no-cache
docker compose up -d
```

### Problème de connexion SSH depuis GitHub Actions

```bash
# Vérifier que la clé SSH est correcte
cat ~/.ssh/authorized_keys

# Tester la connexion manuellement
ssh -i ~/.ssh/id_rsa root@VOTRE_VPS_IP
```

### Port 8003 inaccessible

```bash
# Vérifier que le conteneur écoute sur le bon port
docker compose ps
netstat -tulpn | grep 8003

# Vérifier le pare-feu
ufw status
ufw allow 8003/tcp
```

### Le service consomme trop de mémoire

```bash
# Voir l'utilisation des ressources
docker stats

# Redémarrer le service
docker compose restart

# Ajouter des limites de ressources dans docker-compose.yml
```

### Mise à jour des dépendances

```bash
# Reconstruire l'image avec les nouvelles dépendances
docker compose build --no-cache
docker compose up -d
```

---

## Support

Pour toute question ou problème :
- Consultez les logs : `docker compose logs -f`
- Vérifiez le statut : `docker compose ps`
- Ouvrez une issue sur GitHub

---

## Architecture

```
┌─────────────────┐
│  GitHub Push    │
│   (main branch) │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ GitHub Actions  │
│   Workflow      │
└────────┬────────┘
         │
         │ SSH + rsync
         v
┌─────────────────┐
│      VPS        │
│                 │
│  ┌───────────┐  │
│  │  Docker   │  │
│  │ Compose   │  │
│  └─────┬─────┘  │
│        │        │
│        v        │
│  ┌───────────┐  │
│  │ Container │  │
│  │ (FastAPI) │  │
│  │  :8003    │  │
│  └───────────┘  │
└─────────────────┘
```
