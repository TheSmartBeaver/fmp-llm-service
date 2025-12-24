# Configuration Firebase Cloud Messaging (FCM)

Ce guide explique comment configurer et utiliser Firebase Cloud Messaging pour envoyer des notifications push aux appareils des utilisateurs.

## 🔧 Configuration Backend (Python/FastAPI)

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Configuration Firebase

1. Allez sur [Firebase Console](https://console.firebase.google.com/)
2. Sélectionnez votre projet
3. Allez dans **Paramètres du projet** > **Comptes de service**
4. Cliquez sur **Générer une nouvelle clé privée**
5. Téléchargez le fichier JSON

### 3. Configuration du fichier .env

Ajoutez le chemin vers votre fichier de credentials Firebase dans le fichier `.env` :

```env
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
```

### 4. Migration de la base de données

Exécutez la migration SQL pour créer la table `DeviceTokens` :

```bash
psql -U postgres -d FlashMemProDb -f migrations/create_device_tokens_table.sql
```

## 📱 Intégration Flutter (Frontend)

### 1. Installation du package

Ajoutez dans votre `pubspec.yaml` :

```yaml
dependencies:
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.9
```

### 2. Configuration Firebase dans Flutter

#### Android (`android/app/build.gradle`)

```gradle
dependencies {
    implementation platform('com.google.firebase:firebase-bom:32.7.0')
    implementation 'com.google.firebase:firebase-messaging'
}
```

#### iOS (`ios/Runner/AppDelegate.swift`)

```swift
import Firebase
import FirebaseMessaging

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    FirebaseApp.configure()
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

### 3. Code Flutter pour gérer les notifications

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FCMService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  String? _fcmToken;

  // Initialiser Firebase et demander les permissions
  Future<void> initialize() async {
    await Firebase.initializeApp();

    // Demander la permission pour les notifications
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ Permission accordée pour les notifications');

      // Obtenir le token FCM
      _fcmToken = await _firebaseMessaging.getToken();
      print('📱 FCM Token: $_fcmToken');

      // Enregistrer le token sur le backend
      if (_fcmToken != null) {
        await registerDeviceToken(_fcmToken!);
      }
    }

    // Écouter les changements de token
    _firebaseMessaging.onTokenRefresh.listen((newToken) {
      print('🔄 Token FCM mis à jour: $newToken');
      registerDeviceToken(newToken);
    });

    // Gérer les notifications quand l'app est au premier plan
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📥 Notification reçue (foreground)');
      _handleNotification(message);
    });

    // Gérer les clics sur les notifications
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('🖱️ Notification cliquée');
      _handleNotificationClick(message);
    });

    // Gérer le cas où l'app est lancée depuis une notification
    RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      print('🚀 App lancée depuis une notification');
      _handleNotificationClick(initialMessage);
    }
  }

  // Enregistrer le token sur le backend
  Future<void> registerDeviceToken(String token) async {
    try {
      final response = await http.post(
        Uri.parse('http://your-backend-url/devices/register'),
        headers: {
          'Content-Type': 'application/json',
          'X-Auth-Uid': 'YOUR_AUTH_UID', // À remplacer par l'UID réel de l'utilisateur
        },
        body: jsonEncode({
          'fcm_token': token,
          'device_type': 'android', // ou 'ios', 'web'
          'device_name': 'Mon Appareil',
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Token enregistré avec succès');
      } else {
        print('❌ Erreur lors de l\'enregistrement du token: ${response.body}');
      }
    } catch (e) {
      print('❌ Exception lors de l\'enregistrement du token: $e');
    }
  }

  // Gérer la notification reçue (foreground)
  void _handleNotification(RemoteMessage message) {
    print('Titre: ${message.notification?.title}');
    print('Body: ${message.notification?.body}');
    print('Data: ${message.data}');

    // Extraire les données de la notification
    if (message.data.containsKey('event')) {
      String event = message.data['event'];

      if (event == 'course_material_generated') {
        String taskId = message.data['task_id'];
        String supportsData = message.data['data'];

        // Traiter les données
        print('📚 Supports de cours générés pour task_id: $taskId');

        // Décoder les supports de cours
        List<dynamic> supports = jsonDecode(supportsData);
        print('Nombre de supports: ${supports.length}');

        // Naviguer vers l'écran approprié ou mettre à jour l'UI
        // Navigator.pushNamed(context, '/course-materials', arguments: supports);
      }
    }
  }

  // Gérer le clic sur la notification
  void _handleNotificationClick(RemoteMessage message) {
    print('🖱️ Notification cliquée: ${message.data}');

    if (message.data.containsKey('event')) {
      String event = message.data['event'];
      String taskId = message.data['task_id'];

      if (event == 'course_material_generated') {
        String supportsData = message.data['data'];
        List<dynamic> supports = jsonDecode(supportsData);

        // Naviguer vers l'écran des supports de cours
        // Navigator.pushNamed(context, '/course-materials', arguments: {
        //   'task_id': taskId,
        //   'supports': supports,
        // });
      } else if (event == 'course_material_error') {
        String error = message.data['error'];
        // Afficher un message d'erreur
        // showErrorDialog(error);
      }
    }
  }
}
```

### 4. Utilisation dans votre app Flutter

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialiser FCM
  final fcmService = FCMService();
  await fcmService.initialize();

  runApp(MyApp());
}
```

## 🔔 Format des notifications

### Notification de succès (course_material_generated)

```json
{
  "notification": {
    "title": "Supports de cours générés",
    "body": "3 support(s) de cours ont été générés avec succès"
  },
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "event": "course_material_generated",
    "templates_used": "15",
    "supports_count": "3",
    "data": "[{...}, {...}, {...}]",
    "prompt": "Le prompt utilisé pour la génération"
  }
}
```

### Notification d'erreur (course_material_error)

```json
{
  "notification": {
    "title": "Erreur de génération",
    "body": "Une erreur s'est produite lors de la génération des supports de cours"
  },
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "event": "course_material_error",
    "error": "Description de l'erreur"
  }
}
```

## 📡 API Endpoints

### Enregistrer un appareil

```bash
POST /devices/register
Headers:
  X-Auth-Uid: <user_auth_uid>
  Content-Type: application/json

Body:
{
  "fcm_token": "fGHj8kL3R...token_example",
  "device_type": "android",  // "android", "ios", ou "web"
  "device_name": "Samsung Galaxy S21"
}
```

### Lister les appareils de l'utilisateur

```bash
GET /devices/
Headers:
  X-Auth-Uid: <user_auth_uid>
```

### Mettre à jour un appareil

```bash
PUT /devices/{device_id}
Headers:
  X-Auth-Uid: <user_auth_uid>
  Content-Type: application/json

Body:
{
  "fcm_token": "new_token",
  "device_name": "Mon nouveau téléphone",
  "is_active": true
}
```

### Supprimer un appareil

```bash
DELETE /devices/{device_id}
Headers:
  X-Auth-Uid: <user_auth_uid>
```

## 🧪 Tests

### Tester l'envoi d'une notification

Vous pouvez tester en appelant l'endpoint de génération de support de cours :

```bash
POST /course_material/generate_CELERY
Headers:
  X-Auth-Uid: <user_auth_uid>
  Content-Type: application/json

Body:
{
  "context_entry": {...},
  "textual_content": "...",
  "medias": [...]
}
```

Une notification FCM sera envoyée automatiquement une fois la génération terminée.

## 🔍 Dépannage

### Problème : Pas de token FCM reçu

- Vérifiez que Firebase est correctement configuré dans votre projet Flutter
- Assurez-vous que les permissions de notification sont accordées
- Sur iOS, vérifiez que les Push Notifications sont activées dans Xcode

### Problème : Notifications non reçues

- Vérifiez que le token est bien enregistré sur le backend
- Vérifiez que l'appareil est marqué comme `is_active: true`
- Consultez les logs du worker Celery pour voir si les notifications sont bien envoyées
- Vérifiez les logs Firebase dans la console Firebase

### Problème : Erreur d'initialisation Firebase Admin SDK

- Vérifiez que le chemin `FIREBASE_CREDENTIALS_PATH` dans `.env` est correct
- Assurez-vous que le fichier JSON de credentials existe et est valide
- Vérifiez les permissions du fichier

## 📚 Ressources

- [Firebase Cloud Messaging Documentation](https://firebase.google.com/docs/cloud-messaging)
- [Firebase Flutter Package](https://firebase.flutter.dev/docs/messaging/overview)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
