# Guide de dépannage - Service ne répond pas

## Symptôme
Le port 8003 est ouvert mais l'API ne répond pas (HTTP 000).

## Diagnostic étape par étape

### 1. Vérifier que le conteneur tourne
```bash
docker compose ps
```

**Attendu :** Le statut doit être "Up" et non "Restarting" ou "Exited"

Si le conteneur redémarre en boucle ou est arrêté, passez à l'étape 2.

### 2. Examiner les logs
```bash
docker compose logs --tail=100 fmp-llm-service
```

**Cherchez :**
- Erreurs Python (Traceback, Exception)
- Erreurs de dépendances manquantes
- Erreurs de connexion à la base de données
- Messages "Application startup complete"

**Solutions courantes :**

#### Erreur : Module manquant
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution :** Ajoutez la dépendance dans `requirements.txt` et rebuilez :
```bash
docker compose down
docker compose up -d --build
```

#### Erreur : Variable d'environnement manquante
```
KeyError: 'OPENAI_API_KEY'
```
**Solution :** Vérifiez que le fichier `.env` existe et contient toutes les variables nécessaires :
```bash
cat .env
# Ajoutez les variables manquantes
docker compose restart
```

#### Erreur : Connexion base de données
```
could not connect to server: Connection refused
```
**Solution :** Vérifiez que votre `DATABASE_URL` pointe vers la bonne adresse (utilisez l'IP du VPS, pas localhost) :
```env
DATABASE_URL=postgresql://user:password@46.202.134.247:5432/dbname
```

### 3. Vérifier le binding réseau
```bash
# Voir sur quel port le conteneur écoute
docker compose exec fmp-llm-service netstat -tuln | grep 8003
```

**Attendu :** Devrait montrer `0.0.0.0:8003` et NON `127.0.0.1:8003`

Si vous voyez `127.0.0.1:8003`, le problème est que uvicorn écoute uniquement sur localhost à l'intérieur du conteneur.

**Vérification dans le Dockerfile :**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```
Le `--host 0.0.0.0` est crucial !

### 4. Tester depuis l'intérieur du conteneur
```bash
# Entrer dans le conteneur
docker compose exec fmp-llm-service bash

# Tester depuis l'intérieur
curl http://localhost:8003/docs
# OU
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8003/docs').read()[:100])"

# Sortir du conteneur
exit
```

**Si ça marche à l'intérieur mais pas à l'extérieur :**
- Problème de mapping de ports
- Problème de pare-feu

### 5. Vérifier le mapping des ports
```bash
docker port fmp-llm-service
```

**Attendu :**
```
8003/tcp -> 0.0.0.0:8003
```

### 6. Vérifier le pare-feu du VPS
```bash
# Vérifier le statut du pare-feu
ufw status

# Si le port 8003 n'est pas autorisé
ufw allow 8003/tcp
```

### 7. Vérifier les processus qui écoutent sur le port
```bash
# Sur le VPS (hors Docker)
ss -tuln | grep 8003
# OU
netstat -tuln | grep 8003
```

**Attendu :** Devrait montrer Docker écoutant sur `0.0.0.0:8003`

Si un autre service utilise le port :
```bash
# Trouver le processus
lsof -i :8003

# Option 1: Arrêter l'autre service
# Option 2: Changer le port dans docker-compose.yml
# ports:
#   - "8004:8003"  # Port 8004 sur l'hôte, 8003 dans le conteneur
```

### 8. Reconstruire complètement
Si rien ne fonctionne, nettoyage complet :

```bash
# Arrêter et supprimer tout
docker compose down -v

# Supprimer l'image
docker rmi fmp-llm-service_fmp-llm-service

# Reconstruire sans cache
docker compose build --no-cache

# Redémarrer
docker compose up -d

# Suivre les logs
docker compose logs -f
```

## Commandes de diagnostic rapide

```bash
# Script complet de diagnostic
echo "=== Docker Status ==="
docker compose ps

echo -e "\n=== Derniers logs ==="
docker compose logs --tail=50

echo -e "\n=== Ports mappés ==="
docker port fmp-llm-service

echo -e "\n=== Processus écoutant sur 8003 ==="
ss -tuln | grep 8003

echo -e "\n=== Test HTTP interne ==="
docker compose exec fmp-llm-service curl -s http://localhost:8003/ | head -c 100

echo -e "\n=== Pare-feu ==="
ufw status | grep 8003
```

## Problèmes spécifiques

### Le healthcheck échoue
Si `docker compose ps` montre "unhealthy" :

1. Le healthcheck est trop strict ou démarre trop tôt
2. Solution temporaire : Commentez le healthcheck dans `docker-compose.yml`
```yaml
# healthcheck:
#   test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8003/docs')"]
#   interval: 30s
#   timeout: 10s
#   retries: 3
#   start_period: 40s
```

3. Reconstruisez :
```bash
docker compose up -d --build
```

### Le conteneur démarre puis s'arrête immédiatement
Causes possibles :
1. Erreur Python au démarrage (voir logs)
2. Commande CMD incorrecte dans le Dockerfile
3. Dépendances manquantes

**Debug mode :**
```bash
# Démarrer le conteneur sans le démarrage automatique
docker compose run --rm fmp-llm-service bash

# À l'intérieur, lancer manuellement
uvicorn app.main:app --host 0.0.0.0 --port 8003

# Observer les erreurs
```

### Timeout lors du démarrage
Si l'application prend trop de temps à démarrer (chargement de modèles ML) :

1. Augmentez le `start_period` du healthcheck
```yaml
healthcheck:
  start_period: 120s  # 2 minutes
```

2. Ou désactivez temporairement le healthcheck

## Vérification finale

Une fois corrigé, testez :

```bash
# Test 1: Depuis le VPS
curl http://localhost:8003/docs

# Test 2: Depuis l'extérieur
curl http://VOTRE_IP_VPS:8003/docs

# Test 3: Dans le navigateur
# http://VOTRE_IP_VPS:8003/docs
```

## Contact / Support

Si le problème persiste après ces étapes :
1. Récupérez les logs complets : `docker compose logs > logs.txt`
2. Récupérez la configuration : `docker compose config > config.yml`
3. Ouvrez une issue avec ces fichiers
