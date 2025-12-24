// Service Flutter complet pour gérer les notifications FCM
// À placer dans votre projet Flutter : lib/services/fcm_service.dart

import 'dart:convert';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Handler pour les notifications en background
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('📥 Notification en background: ${message.messageId}');
}

class FCMService {
  static final FCMService _instance = FCMService._internal();
  factory FCMService() => _instance;
  FCMService._internal();

  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  String? _fcmToken;
  String? _authUid;
  String? _backendUrl;

  // Callbacks personnalisables
  Function(RemoteMessage)? onNotificationReceived;
  Function(RemoteMessage)? onNotificationClicked;

  String? get fcmToken => _fcmToken;

  /// Initialiser le service FCM
  Future<void> initialize({
    required String backendUrl,
    required String authUid,
    Function(RemoteMessage)? onNotificationReceived,
    Function(RemoteMessage)? onNotificationClicked,
  }) async {
    _backendUrl = backendUrl;
    _authUid = authUid;
    this.onNotificationReceived = onNotificationReceived;
    this.onNotificationClicked = onNotificationClicked;

    await Firebase.initializeApp();

    // Configurer le handler pour les notifications en background
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Demander les permissions
    await _requestPermissions();

    // Obtenir le token FCM
    await _getFCMToken();

    // Configurer les listeners
    _setupNotificationListeners();

    // Gérer le cas où l'app est lancée depuis une notification
    _handleInitialMessage();
  }

  /// Demander les permissions pour les notifications
  Future<void> _requestPermissions() async {
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ Permissions de notification accordées');
    } else if (settings.authorizationStatus == AuthorizationStatus.provisional) {
      print('⚠️ Permissions provisoires accordées');
    } else {
      print('❌ Permissions de notification refusées');
    }
  }

  /// Obtenir le token FCM
  Future<void> _getFCMToken() async {
    try {
      _fcmToken = await _firebaseMessaging.getToken();
      if (_fcmToken != null) {
        print('📱 FCM Token obtenu: ${_fcmToken!.substring(0, 20)}...');
        await registerDevice(_fcmToken!);
      } else {
        print('⚠️ Impossible d\'obtenir le token FCM');
      }
    } catch (e) {
      print('❌ Erreur lors de l\'obtention du token FCM: $e');
    }
  }

  /// Configurer les listeners pour les notifications
  void _setupNotificationListeners() {
    // Écouter les changements de token
    _firebaseMessaging.onTokenRefresh.listen((newToken) {
      print('🔄 Token FCM mis à jour');
      _fcmToken = newToken;
      registerDevice(newToken);
    });

    // Gérer les notifications au premier plan
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📥 Notification reçue (foreground)');
      _handleForegroundNotification(message);
      onNotificationReceived?.call(message);
    });

    // Gérer les clics sur les notifications
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('🖱️ Notification cliquée');
      _handleNotificationTap(message);
      onNotificationClicked?.call(message);
    });
  }

  /// Gérer le cas où l'app est lancée depuis une notification
  Future<void> _handleInitialMessage() async {
    RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      print('🚀 App lancée depuis une notification');
      _handleNotificationTap(initialMessage);
      onNotificationClicked?.call(initialMessage);
    }
  }

  /// Gérer les notifications au premier plan
  void _handleForegroundNotification(RemoteMessage message) {
    print('Notification: ${message.notification?.title}');
    print('Body: ${message.notification?.body}');
    print('Data: ${message.data}');
  }

  /// Gérer le clic sur une notification
  void _handleNotificationTap(RemoteMessage message) {
    print('Données de la notification: ${message.data}');

    if (message.data.containsKey('event')) {
      String event = message.data['event'];
      print('Événement: $event');

      // Vous pouvez ajouter ici la logique de navigation
      // basée sur le type d'événement
    }
  }

  /// Enregistrer l'appareil sur le backend
  Future<bool> registerDevice(
    String token, {
    String deviceType = 'android',
    String? deviceName,
  }) async {
    if (_backendUrl == null || _authUid == null) {
      print('❌ Backend URL ou Auth UID non configuré');
      return false;
    }

    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/devices/register'),
        headers: {
          'Content-Type': 'application/json',
          'X-Auth-Uid': _authUid!,
        },
        body: jsonEncode({
          'fcm_token': token,
          'device_type': deviceType,
          'device_name': deviceName ?? 'Flutter Device',
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Appareil enregistré avec succès');
        return true;
      } else {
        print('❌ Erreur lors de l\'enregistrement: ${response.statusCode}');
        print('Body: ${response.body}');
        return false;
      }
    } catch (e) {
      print('❌ Exception lors de l\'enregistrement: $e');
      return false;
    }
  }

  /// Récupérer la liste des appareils enregistrés
  Future<List<Device>> getDevices() async {
    if (_backendUrl == null || _authUid == null) {
      print('❌ Backend URL ou Auth UID non configuré');
      return [];
    }

    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/devices/'),
        headers: {
          'X-Auth-Uid': _authUid!,
        },
      );

      if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Device.fromJson(json)).toList();
      } else {
        print('❌ Erreur lors de la récupération des appareils: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('❌ Exception lors de la récupération: $e');
      return [];
    }
  }

  /// Supprimer un appareil
  Future<bool> deleteDevice(String deviceId) async {
    if (_backendUrl == null || _authUid == null) {
      print('❌ Backend URL ou Auth UID non configuré');
      return false;
    }

    try {
      final response = await http.delete(
        Uri.parse('$_backendUrl/devices/$deviceId'),
        headers: {
          'X-Auth-Uid': _authUid!,
        },
      );

      if (response.statusCode == 200) {
        print('✅ Appareil supprimé avec succès');
        return true;
      } else {
        print('❌ Erreur lors de la suppression: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      print('❌ Exception lors de la suppression: $e');
      return false;
    }
  }

  /// Extraire les données d'une notification de type course_material_generated
  CourseMaterialNotificationData? extractCourseMaterialData(RemoteMessage message) {
    if (message.data['event'] != 'course_material_generated') {
      return null;
    }

    try {
      return CourseMaterialNotificationData(
        taskId: message.data['task_id'] ?? '',
        templatesUsed: int.tryParse(message.data['templates_used'] ?? '0') ?? 0,
        supportsCount: int.tryParse(message.data['supports_count'] ?? '0') ?? 0,
        supports: jsonDecode(message.data['data'] ?? '[]'),
        prompt: message.data['prompt'] ?? '',
      );
    } catch (e) {
      print('❌ Erreur lors de l\'extraction des données: $e');
      return null;
    }
  }
}

// Modèle pour les appareils
class Device {
  final String sku;
  final String appUserSku;
  final String fcmToken;
  final String deviceType;
  final String? deviceName;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastUsed;

  Device({
    required this.sku,
    required this.appUserSku,
    required this.fcmToken,
    required this.deviceType,
    this.deviceName,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.lastUsed,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      sku: json['sku'],
      appUserSku: json['app_user_sku'],
      fcmToken: json['fcm_token'],
      deviceType: json['device_type'],
      deviceName: json['device_name'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      lastUsed: json['last_used'] != null ? DateTime.parse(json['last_used']) : null,
    );
  }
}

// Modèle pour les données de notification de support de cours
class CourseMaterialNotificationData {
  final String taskId;
  final int templatesUsed;
  final int supportsCount;
  final List<dynamic> supports;
  final String prompt;

  CourseMaterialNotificationData({
    required this.taskId,
    required this.templatesUsed,
    required this.supportsCount,
    required this.supports,
    required this.prompt,
  });
}

// Exemple d'utilisation dans votre app Flutter
void exampleUsage() async {
  final fcmService = FCMService();

  // Initialiser
  await fcmService.initialize(
    backendUrl: 'http://your-backend-url.com',
    authUid: 'user_auth_uid_from_firebase_auth',
    onNotificationReceived: (message) {
      // Gérer la notification reçue
      print('Notification reçue: ${message.notification?.title}');

      // Extraire les données si c'est une notification de support de cours
      final data = fcmService.extractCourseMaterialData(message);
      if (data != null) {
        print('Supports générés: ${data.supportsCount}');
        // Mettre à jour l'UI, afficher un snackbar, etc.
      }
    },
    onNotificationClicked: (message) {
      // Gérer le clic sur la notification
      print('Notification cliquée: ${message.data}');

      // Naviguer vers l'écran approprié
      final data = fcmService.extractCourseMaterialData(message);
      if (data != null) {
        // Navigator.pushNamed(context, '/course-materials', arguments: data);
      }
    },
  );

  // Récupérer la liste des appareils
  final devices = await fcmService.getDevices();
  print('Nombre d\'appareils: ${devices.length}');
}
