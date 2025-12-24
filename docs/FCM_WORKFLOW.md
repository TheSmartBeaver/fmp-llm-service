# Workflow FCM - Récupération des supports de cours

Ce document explique comment l'application mobile Flutter doit gérer les notifications FCM et récupérer les supports de cours générés.

---

## 📋 Architecture du flux

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Demande de génération                  │
│   App Mobile ────POST /course_material/generate_CELERY───►  │
│                         Backend API                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Retourne: {"task_id": "abc123", "status": "pending"}
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  2. Traitement asynchrone                    │
│              Celery Worker génère les supports              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Lors de la complétion
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Notification FCM envoyée                     │
│   Backend ────────FCM Notification────────► App Mobile      │
│                                                              │
│   Payload: {                                                 │
│     "task_id": "abc123",                                     │
│     "event": "course_material_generated",                    │
│     "supports_count": "3",                                   │
│     "templates_used": "15"                                   │
│   }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ L'app extrait task_id
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           4. Récupération des données complètes              │
│   App Mobile ────GET /course_material/result/{task_id}───►  │
│                         Backend API                          │
│                                                              │
│   Réponse: {                                                 │
│     "status": "SUCCESS",                                     │
│     "result": {                                              │
│       "supports": [...],                                     │
│       "prompt": "...",                                       │
│       "templates_used": 15                                   │
│     }                                                        │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Implémentation Flutter

### 1. Envoyer une demande de génération

```dart
Future<String> generateCourseMaterial(UserEntry userEntry, String authUid) async {
  final response = await http.post(
    Uri.parse('$API_BASE_URL/course_material/generate_CELERY'),
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Uid': authUid,
    },
    body: jsonEncode(userEntry.toJson()),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    String taskId = data['task_id'];

    // Stocker le task_id localement si besoin
    await saveTaskIdLocally(taskId);

    return taskId;
  } else {
    throw Exception('Failed to generate course material');
  }
}
```

### 2. Écouter les notifications FCM

```dart
void setupFirebaseMessaging() {
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    print('Message reçu: ${message.data}');

    if (message.data['event'] == 'course_material_generated') {
      String taskId = message.data['task_id'];
      String supportsCount = message.data['supports_count'];

      // Afficher une notification locale
      showLocalNotification(
        title: 'Supports générés',
        body: '$supportsCount supports de cours disponibles',
      );

      // Récupérer automatiquement les données
      fetchCourseMaterialResult(taskId);
    }
  });

  // Pour les notifications en arrière-plan
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
}

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Background message: ${message.data}');

  if (message.data['event'] == 'course_material_generated') {
    String taskId = message.data['task_id'];
    await fetchCourseMaterialResult(taskId);
  }
}
```

### 3. Récupérer les résultats via l'API

```dart
Future<CourseMaterialResult?> fetchCourseMaterialResult(String taskId) async {
  try {
    final response = await http.get(
      Uri.parse('$API_BASE_URL/course_material/result/$taskId'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      switch (data['status']) {
        case 'SUCCESS':
          // Traiter les supports générés
          List<dynamic> supports = data['result']['supports'];
          String prompt = data['result']['prompt'];
          int templatesUsed = data['result']['templates_used'];

          print('✅ Supports récupérés: ${supports.length} items');

          // Sauvegarder en base de données locale
          await saveSupportsToDatabase(supports);

          // Notifier l'UI
          notifyUIUpdate();

          return CourseMaterialResult.fromJson(data['result']);

        case 'PENDING':
          print('⏳ Génération en cours...');
          // Optionnel: Réessayer après quelques secondes
          await Future.delayed(Duration(seconds: 3));
          return fetchCourseMaterialResult(taskId);

        case 'FAILURE':
          print('❌ Erreur: ${data['error']}');
          showErrorNotification(data['error']);
          return null;

        default:
          print('État: ${data['status']}');
          return null;
      }
    } else {
      throw Exception('Failed to fetch result');
    }
  } catch (e) {
    print('Erreur lors de la récupération: $e');
    return null;
  }
}
```

### 4. Modèle de données Flutter

```dart
class CourseMaterialResult {
  final bool success;
  final List<Support> supports;
  final int templatesUsed;
  final String prompt;

  CourseMaterialResult({
    required this.success,
    required this.supports,
    required this.templatesUsed,
    required this.prompt,
  });

  factory CourseMaterialResult.fromJson(Map<String, dynamic> json) {
    return CourseMaterialResult(
      success: json['success'] ?? true,
      supports: (json['supports'] as List)
          .map((item) => Support.fromJson(item))
          .toList(),
      templatesUsed: json['templates_used'] ?? 0,
      prompt: json['prompt'] ?? '',
    );
  }
}

class Support {
  final Map<String, dynamic> support;
  final String version;

  Support({
    required this.support,
    required this.version,
  });

  factory Support.fromJson(Map<String, dynamic> json) {
    return Support(
      support: json['support'] ?? {},
      version: json['version'] ?? '1.0.0',
    );
  }
}
```

---

## 📊 États possibles de la tâche

| État | Description | Action recommandée |
|------|-------------|-------------------|
| `PENDING` | La tâche est en attente ou en cours | Réessayer après quelques secondes |
| `SUCCESS` | Génération terminée avec succès | Récupérer et afficher les supports |
| `FAILURE` | Erreur lors de la génération | Afficher un message d'erreur |
| `STARTED` | Tâche démarrée (rare) | Attendre la notification FCM |

---

## 🔧 Configuration Firebase

### Dans `firebase_options.dart`

Assurez-vous que votre projet Firebase est bien configuré :

```dart
static const FirebaseOptions android = FirebaseOptions(
  apiKey: 'YOUR_API_KEY',
  appId: 'YOUR_APP_ID',
  messagingSenderId: 'YOUR_SENDER_ID',
  projectId: 'YOUR_PROJECT_ID',
);
```

### Permissions Android (`AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

---

## 🎯 Exemple de flux complet

```dart
// 1. L'utilisateur demande la génération
void onGenerateButtonPressed() async {
  setState(() => isLoading = true);

  try {
    String taskId = await generateCourseMaterial(userEntry, currentUser.authUid);

    print('✅ Tâche lancée: $taskId');

    // Afficher un message à l'utilisateur
    showSnackBar('Génération en cours... Vous recevrez une notification');

  } catch (e) {
    showError('Erreur: $e');
  } finally {
    setState(() => isLoading = false);
  }
}

// 2. L'app reçoit la notification FCM (automatique)
// 3. L'app récupère les données (dans le handler FCM)
// 4. L'UI se met à jour automatiquement
```

---

## ⚠️ Points importants

1. **Limite de taille FCM** : Les notifications ne contiennent QUE les métadonnées (task_id, count, etc.), jamais le contenu complet
2. **Durée de vie des résultats** : Les résultats sont stockés dans Redis. Configurez une durée d'expiration appropriée
3. **Gestion hors ligne** : Si l'app est hors ligne, elle peut récupérer les résultats plus tard via le `task_id`
4. **Retry logic** : Implémentez un mécanisme de retry en cas d'échec réseau

---

## 🧪 Test de l'API

### Avec cURL

```bash
# 1. Générer des supports
curl -X POST http://your-vps:8003/course_material/generate_CELERY \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: your-auth-uid" \
  -d '{
    "context_entry": {...},
    "book_scan_entry": [...],
    ...
  }'

# Réponse: {"task_id": "abc-123", "status": "pending"}

# 2. Récupérer le résultat
curl http://your-vps:8003/course_material/result/abc-123

# Réponse: {"status": "SUCCESS", "result": {...}}
```

---

## 📝 Checklist d'intégration

- [ ] Configurer Firebase Messaging dans l'app Flutter
- [ ] Implémenter l'envoi du device token au backend (`POST /device`)
- [ ] Ajouter le listener FCM avec gestion de `course_material_generated`
- [ ] Implémenter `fetchCourseMaterialResult(taskId)`
- [ ] Créer les modèles de données (`CourseMaterialResult`, `Support`)
- [ ] Tester le flux complet en développement
- [ ] Gérer les cas d'erreur et timeouts
- [ ] Implémenter la sauvegarde locale des supports
- [ ] Ajouter des notifications locales pour l'UX
