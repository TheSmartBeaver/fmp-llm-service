# Guide de Test des Notifications FCM

Ce guide vous explique comment tester l'envoi de notifications FCM à votre application Flutter.

## Prérequis

1. ✅ Votre serveur FastAPI doit être démarré
2. ✅ Votre application Flutter doit avoir enregistré un token FCM via `/devices/register`
3. ✅ Vous devez connaître votre `auth_uid` (Firebase Authentication UID)

## Route de Test

**Endpoint:** `POST /devices/test-notification`

Cette route envoie une notification de test à tous vos appareils actifs.

## Méthode 1: Utiliser le Script Python

Le moyen le plus simple:

```bash
# Installation des dépendances (si nécessaire)
pip install requests

# Envoi d'une notification de test simple
python test_fcm_notification.py --auth-uid "VOTRE_AUTH_UID"

# Notification personnalisée
python test_fcm_notification.py \
  --auth-uid "VOTRE_AUTH_UID" \
  --title "Salut!" \
  --body "Ceci est un test personnalisé" \
  --data '{"action": "open_screen", "screen": "home"}'
```

## Méthode 2: Utiliser cURL

```bash
# Notification de test avec valeurs par défaut
curl -X POST http://localhost:8000/devices/test-notification \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: VOTRE_AUTH_UID" \
  -d '{}'

# Notification personnalisée
curl -X POST http://localhost:8000/devices/test-notification \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: VOTRE_AUTH_UID" \
  -d '{
    "title": "Test FCM",
    "body": "Votre notification de test",
    "data": {
      "test_key": "test_value",
      "action": "test"
    }
  }'
```

## Méthode 3: Utiliser l'interface Swagger/Docs

1. Ouvrez votre navigateur: http://localhost:8000/docs
2. Cherchez la section **devices**
3. Cliquez sur `POST /devices/test-notification`
4. Cliquez sur **Try it out**
5. Remplissez le header `X-Auth-Uid` avec votre auth_uid
6. Modifiez le body de la requête (optionnel)
7. Cliquez sur **Execute**

## Réponse Attendue

Si tout fonctionne correctement, vous devriez recevoir une réponse comme:

```json
{
  "success": true,
  "message": "Notification sent to 1/1 devices",
  "devices_found": 1,
  "active_devices": 1,
  "success_count": 1,
  "failure_count": 0,
  "failed_tokens": []
}
```

### Et sur votre appareil Flutter:

Vous devriez recevoir une notification push ! 🎉

## Payload de la Requête (Optionnel)

```json
{
  "title": "Titre de votre notification",
  "body": "Corps de votre notification",
  "data": {
    "clé_personnalisée": "valeur",
    "autre_clé": "autre_valeur"
  }
}
```

**Note:** Tous les champs sont optionnels. Si vous ne les spécifiez pas:
- `title` par défaut: "Test Notification"
- `body` par défaut: "Ceci est une notification de test depuis fmp-llm-service"
- `data` par défaut: Métadonnées de test automatiques

## Dépannage

### ❌ Erreur: "User not found"
- Vérifiez que votre `auth_uid` est correct
- Assurez-vous que l'utilisateur existe dans la table `AppUsers`

### ❌ Erreur: "No active devices found"
- Votre application Flutter doit d'abord enregistrer un token via `/devices/register`
- Vérifiez que le token est actif (`IsActive = true`)

### ❌ `success_count: 0`, `failure_count: 1`
- Le token FCM est peut-être expiré ou invalide
- Réenregistrez votre appareil depuis l'application Flutter
- Vérifiez les logs du serveur pour plus de détails

### ❌ Erreur: "Connection refused"
- Assurez-vous que le serveur FastAPI est démarré
- Vérifiez l'URL (par défaut: http://localhost:8000)

## Intégration dans Flutter

Pour recevoir les notifications dans votre app Flutter, assurez-vous d'avoir:

1. **Configuré Firebase Cloud Messaging:**
```dart
await FirebaseMessaging.instance.requestPermission();
```

2. **Enregistré le token:**
```dart
String? token = await FirebaseMessaging.instance.getToken();
// Envoyer ce token à /devices/register
```

3. **Écouté les notifications:**
```dart
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Notification reçue: ${message.notification?.title}');
  print('Data: ${message.data}');
});
```

## Exemple de Données Reçues dans Flutter

Quand vous envoyez une notification de test, votre app Flutter reçoit:

```dart
RemoteMessage(
  notification: Notification(
    title: "Test Notification",
    body: "Ceci est une notification de test..."
  ),
  data: {
    "test": "true",
    "timestamp": "2025-12-24T10:30:00.123456",
    "auth_uid": "votre_auth_uid",
    // + vos données personnalisées
  }
)
```

## Prochaines Étapes

Une fois que cette route de test fonctionne, vous pouvez être sûr que:
- ✅ FCM est correctement configuré
- ✅ Les tokens sont bien enregistrés
- ✅ Votre app Flutter peut recevoir les notifications

Vous pouvez maintenant utiliser l'endpoint `/course_material/generate_CELERY` qui enverra automatiquement une notification quand les supports de cours sont générés!
