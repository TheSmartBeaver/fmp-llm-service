"""
Script de test pour envoyer une notification FCM de test
Usage: python examples/test_fcm_notification.py
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fcm_service import FCMService
from dotenv import load_dotenv

def test_send_notification():
    """
    Tester l'envoi d'une notification FCM

    IMPORTANT: Avant d'exécuter ce script:
    1. Configurez FIREBASE_CREDENTIALS_PATH dans votre fichier .env
    2. Remplacez TEST_FCM_TOKEN par un vrai token FCM de votre appareil
    """

    # Charger les variables d'environnement
    load_dotenv()

    # Token FCM de test - À REMPLACER par un vrai token depuis votre appareil Flutter
    TEST_FCM_TOKEN = "YOUR_DEVICE_FCM_TOKEN_HERE"

    if TEST_FCM_TOKEN == "YOUR_DEVICE_FCM_TOKEN_HERE":
        print("❌ Veuillez remplacer TEST_FCM_TOKEN par un vrai token FCM dans ce script")
        print("💡 Vous pouvez obtenir le token depuis votre app Flutter en utilisant:")
        print("   String? token = await FirebaseMessaging.instance.getToken();")
        return

    print("🚀 Initialisation du service FCM...")
    fcm_service = FCMService()

    # Test 1: Notification simple
    print("\n📤 Test 1: Envoi d'une notification simple...")
    success = fcm_service.send_notification(
        token=TEST_FCM_TOKEN,
        title="Test FCM",
        body="Ceci est une notification de test",
        data={
            "test": "true",
            "timestamp": "2025-01-23T10:30:00Z"
        },
        notification_id="test-notification-1"
    )

    if success:
        print("✅ Notification envoyée avec succès")
    else:
        print("❌ Échec de l'envoi de la notification")

    # Test 2: Notification de type course_material_generated
    print("\n📤 Test 2: Envoi d'une notification de support de cours généré...")
    success = fcm_service.send_notification(
        token=TEST_FCM_TOKEN,
        title="Supports de cours générés",
        body="3 support(s) de cours ont été générés avec succès",
        data={
            "task_id": "test-task-123",
            "event": "course_material_generated",
            "templates_used": "15",
            "supports_count": "3",
            "data": '[{"title": "Support 1"}, {"title": "Support 2"}, {"title": "Support 3"}]',
            "prompt": "Test prompt"
        },
        notification_id="test-task-123"
    )

    if success:
        print("✅ Notification de support de cours envoyée avec succès")
    else:
        print("❌ Échec de l'envoi de la notification")

    # Test 3: Notification multicast (plusieurs appareils)
    print("\n📤 Test 3: Envoi d'une notification multicast...")
    result = fcm_service.send_multicast_notification(
        tokens=[TEST_FCM_TOKEN],  # Vous pouvez ajouter plusieurs tokens ici
        title="Notification Multicast",
        body="Cette notification est envoyée à plusieurs appareils",
        data={
            "type": "multicast_test"
        },
        notification_id="multicast-test-1"
    )

    print(f"✅ Succès: {result['success_count']}")
    print(f"❌ Échecs: {result['failure_count']}")
    if result['failed_tokens']:
        print(f"Tokens échoués: {result['failed_tokens']}")

    # Test 4: Message de données uniquement (sans notification visible)
    print("\n📤 Test 4: Envoi d'un message de données uniquement...")
    success = fcm_service.send_data_message(
        token=TEST_FCM_TOKEN,
        data={
            "silent": "true",
            "action": "sync_data",
            "timestamp": "2025-01-23T10:35:00Z"
        }
    )

    if success:
        print("✅ Message de données envoyé avec succès")
    else:
        print("❌ Échec de l'envoi du message de données")

    print("\n✨ Tests terminés!")

def test_invalid_token():
    """
    Tester le comportement avec un token invalide
    """
    print("\n🧪 Test avec un token invalide...")
    fcm_service = FCMService()

    success = fcm_service.send_notification(
        token="INVALID_TOKEN_FOR_TESTING",
        title="Test",
        body="Ce message ne devrait pas être envoyé",
        data={}
    )

    if not success:
        print("✅ Le service a correctement géré le token invalide")
    else:
        print("⚠️ Le service n'a pas détecté le token invalide")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Script de test FCM")
    print("=" * 60)

    # Vérifier que Firebase est configuré
    firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not firebase_path:
        print("❌ FIREBASE_CREDENTIALS_PATH non configuré dans .env")
        print("💡 Ajoutez cette ligne à votre fichier .env:")
        print("   FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json")
        sys.exit(1)

    if not os.path.exists(firebase_path):
        print(f"❌ Fichier Firebase credentials non trouvé: {firebase_path}")
        sys.exit(1)

    print(f"✅ Firebase credentials trouvé: {firebase_path}")

    try:
        test_send_notification()
        test_invalid_token()
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
