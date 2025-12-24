# Exemples et Tests

Ce dossier contient des exemples et scripts pour tester les fonctionnalités du service.

## 📁 Contenu

### 1. `test_fcm_examples.sh`
Script bash avec plusieurs exemples de tests de notifications FCM.

**Usage:**
```bash
# 1. Éditer le script et remplacer VOTRE_AUTH_UID
nano examples/test_fcm_examples.sh

# 2. Exécuter tous les exemples
./examples/test_fcm_examples.sh
```

**Contenu:**
- Notification simple
- Notification personnalisée
- Notification avec données de navigation
- Notification d'erreur
- Liste des appareils enregistrés

### 2. `FCM_Test_Collection.json`
Collection pour Thunder Client (VS Code) ou Postman.

**Import dans Thunder Client:**
1. Ouvrir VS Code
2. Aller dans l'extension Thunder Client
3. Cliquer sur "Collections" → Menu (⋮) → "Import"
4. Sélectionner `FCM_Test_Collection.json`
5. Configurer la variable d'environnement `AUTH_UID`

**Import dans Postman:**
1. Ouvrir Postman
2. File → Import
3. Sélectionner `FCM_Test_Collection.json`
4. Configurer la variable `AUTH_UID` dans l'environnement

**Requêtes disponibles:**
- Test Notification - Simple
- Test Notification - Personnalisée
- Test Notification - Avec Données
- Liste des Appareils
- Enregistrer un Appareil

## 🚀 Démarrage Rapide

### Prérequis
1. Serveur FastAPI démarré: `uvicorn app.main:app --reload`
2. Auth UID Firebase disponible
3. Application Flutter avec FCM configuré

### Méthode 1: Script Python (Recommandé)
```bash
# Depuis la racine du projet
python test_fcm_notification.py --auth-uid "VOTRE_AUTH_UID"
```

### Méthode 2: Script Bash
```bash
# Éditer et exécuter
./examples/test_fcm_examples.sh
```

### Méthode 3: cURL Direct
```bash
curl -X POST http://localhost:8000/devices/test-notification \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: VOTRE_AUTH_UID" \
  -d '{
    "title": "Test",
    "body": "Ma notification de test"
  }'
```

## 📱 Workflow Complet

### 1. Enregistrer un appareil (depuis Flutter)
```dart
String? token = await FirebaseMessaging.instance.getToken();
await registerDevice(token);
```

### 2. Tester la notification
```bash
python test_fcm_notification.py --auth-uid "votre_uid"
```

### 3. Vérifier la réception
- La notification apparaît sur votre appareil Flutter
- Vérifiez les logs du serveur pour le statut d'envoi

### 4. Tester avec génération de cours
```bash
curl -X POST http://localhost:8000/course_material/generate_CELERY \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: VOTRE_AUTH_UID" \
  -d '{
    "context_entry": {...},
    "book_scan_entry": [...],
    ...
  }'
```
→ Notification automatique quand la génération est terminée!

## 🔧 Dépannage

### Aucun appareil trouvé
```bash
# Vérifier les appareils enregistrés
curl -X GET http://localhost:8000/devices/ \
  -H "X-Auth-Uid: VOTRE_AUTH_UID"
```

### Token FCM invalide
- Réenregistrer l'appareil depuis Flutter
- Vérifier que le token n'a pas expiré

### Notification non reçue
1. Vérifier les logs serveur
2. Vérifier les permissions FCM dans Flutter
3. Tester sur un autre appareil

## 📚 Documentation Complète

- Guide complet: [`../FCM_TEST_GUIDE.md`](../FCM_TEST_GUIDE.md)
- Configuration FCM: [`../FCM_SETUP.md`](../FCM_SETUP.md)
- Documentation API: http://localhost:8000/docs

## ⚙️ Variables d'Environnement

Pour utiliser ces exemples, vous aurez besoin de:

| Variable | Description | Exemple |
|----------|-------------|---------|
| `AUTH_UID` | Firebase Auth UID | `abc123...xyz` |
| `BASE_URL` | URL du serveur | `http://localhost:8000` |
| `FCM_TOKEN` | Token FCM de l'appareil | `dXy9z...` |

## 🎯 Prochaines Étapes

1. ✅ Tester la route `/devices/test-notification`
2. ✅ Vérifier la réception sur Flutter
3. ✅ Tester `/course_material/generate_CELERY`
4. ✅ Implémenter la gestion des notifications dans Flutter
5. ✅ Configurer les actions de navigation selon les données reçues
