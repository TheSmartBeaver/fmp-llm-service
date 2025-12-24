#!/usr/bin/env python3
"""
Script de test pour envoyer une notification FCM à vos appareils.

Usage:
    python test_fcm_notification.py --auth-uid YOUR_AUTH_UID
    python test_fcm_notification.py --auth-uid YOUR_AUTH_UID --title "Mon titre" --body "Mon message"
"""

import requests
import argparse
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Changez si votre serveur est ailleurs
ENDPOINT = "/devices/test-notification"


def send_test_notification(auth_uid: str, title: str = None, body: str = None, data: dict = None):
    """
    Envoie une notification de test à tous les appareils actifs de l'utilisateur.

    Args:
        auth_uid: L'AuthentUid de l'utilisateur
        title: Titre de la notification (optionnel)
        body: Corps de la notification (optionnel)
        data: Données additionnelles (optionnel)
    """
    url = f"{BASE_URL}{ENDPOINT}"

    # Préparer le payload
    payload = {}
    if title:
        payload["title"] = title
    if body:
        payload["body"] = body
    if data:
        payload["data"] = data

    # Préparer les headers
    headers = {
        "X-Auth-Uid": auth_uid,
        "Content-Type": "application/json"
    }

    print(f"🚀 Envoi de la notification de test...")
    print(f"   URL: {url}")
    print(f"   Auth UID: {auth_uid}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()

        print("✅ Réponse reçue:")
        print(json.dumps(result, indent=2))
        print()

        if result.get("success"):
            print(f"🎉 Notification envoyée avec succès!")
            print(f"   📱 Appareils trouvés: {result.get('devices_found')}")
            print(f"   ✅ Appareils actifs: {result.get('active_devices')}")
            print(f"   📤 Envois réussis: {result.get('success_count')}")
            print(f"   ❌ Envois échoués: {result.get('failure_count')}")

            if result.get("failed_tokens"):
                print(f"   ⚠️  Tokens en échec: {len(result.get('failed_tokens'))}")
        else:
            print(f"⚠️  {result.get('message')}")

    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        try:
            error_detail = e.response.json()
            print(f"   Détails: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"   Réponse: {e.response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter au serveur {BASE_URL}")
        print(f"   Vérifiez que le serveur FastAPI est bien démarré.")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Envoie une notification FCM de test à vos appareils Flutter"
    )
    parser.add_argument(
        "--auth-uid",
        required=True,
        help="Votre AuthentUid (Firebase Auth UID)"
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Titre de la notification (défaut: 'Test Notification')"
    )
    parser.add_argument(
        "--body",
        default=None,
        help="Corps de la notification (défaut: message de test)"
    )
    parser.add_argument(
        "--data",
        default=None,
        help="Données JSON additionnelles (ex: '{\"key\": \"value\"}')"
    )
    parser.add_argument(
        "--url",
        default=BASE_URL,
        help=f"URL de base du serveur (défaut: {BASE_URL})"
    )

    args = parser.parse_args()

    # Mettre à jour l'URL si fournie
    global BASE_URL
    BASE_URL = args.url

    # Parser les données JSON si fournies
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"❌ Erreur: Les données JSON sont invalides")
            return

    send_test_notification(
        auth_uid=args.auth_uid,
        title=args.title,
        body=args.body,
        data=data
    )


if __name__ == "__main__":
    main()
