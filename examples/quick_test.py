#!/usr/bin/env python3
"""
Test rapide des notifications FCM.
Simple et direct - parfait pour un test rapide!
"""

import requests
import sys

# ⚠️ CHANGEZ CETTE VALEUR AVEC VOTRE AUTH_UID
AUTH_UID = "VOTRE_AUTH_UID"

# Configuration
BASE_URL = "http://localhost:8000"


def test_notification():
    """Envoie une notification de test simple."""

    if AUTH_UID == "VOTRE_AUTH_UID":
        print("❌ ERREUR: Veuillez modifier AUTH_UID dans ce fichier")
        print("   Ligne 11: AUTH_UID = \"votre_vrai_auth_uid\"")
        sys.exit(1)

    print(f"🚀 Envoi d'une notification de test...")
    print(f"   Auth UID: {AUTH_UID}")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/devices/test-notification",
            json={
                "title": "🎉 Test FCM",
                "body": "Si vous voyez cette notification, tout fonctionne!"
            },
            headers={"X-Auth-Uid": AUTH_UID}
        )

        response.raise_for_status()
        result = response.json()

        print("✅ Réponse:")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   Appareils actifs: {result['active_devices']}")
        print(f"   Envois réussis: {result['success_count']}")

        if result['success']:
            print("\n🎉 Notification envoyée avec succès!")
            print("   Vérifiez votre application Flutter 📱")
        else:
            print(f"\n⚠️  {result['message']}")

    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Vérifiez que le serveur est démarré:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    test_notification()
