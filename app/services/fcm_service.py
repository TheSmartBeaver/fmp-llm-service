import os
import json
from typing import Dict, List, Optional
#import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv

load_dotenv()

class FCMService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FCMService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not FCMService._initialized:
            self._initialize_firebase()
            FCMService._initialized = True

    def _initialize_firebase(self):
        try:
            firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

            if not firebase_credentials_path:
                print("⚠️ FIREBASE_CREDENTIALS_PATH not set in environment variables")
                return

            if not os.path.exists(firebase_credentials_path):
                print(f"⚠️ Firebase credentials file not found at: {firebase_credentials_path}")
                return

            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized successfully")
        except ValueError as e:
            if "already exists" in str(e):
                print("ℹ️ Firebase Admin SDK already initialized")
            else:
                raise
        except Exception as e:
            print(f"❌ Error initializing Firebase Admin SDK: {str(e)}")
            raise

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        notification_id: Optional[str] = None
    ) -> bool:
        try:
            notification = messaging.Notification(
                title=title,
                body=body
            )

            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    tag=notification_id
                )
            )

            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        content_available=True,
                        category='COURSE_MATERIAL_GENERATED'
                    )
                )
            )

            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=token,
                android=android_config,
                apns=apns_config
            )

            response = messaging.send(message)
            print(f"✅ Successfully sent FCM message: {response}")
            return True

        except Exception as e:
            print(f"❌ Error sending FCM notification: {str(e)}")
            return False

    def send_multicast_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        notification_id: Optional[str] = None
    ) -> Dict[str, any]:
        try:
            if not tokens:
                print("⚠️ No tokens provided for multicast notification")
                return {"success_count": 0, "failure_count": 0, "failed_tokens": []}

            notification = messaging.Notification(
                title=title,
                body=body
            )

            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    tag=notification_id
                )
            )

            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        content_available=True,
                        category='COURSE_MATERIAL_GENERATED'
                    )
                )
            )

            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=tokens,
                android=android_config,
                apns=apns_config
            )

            response = messaging.send_multicast(message)

            failed_tokens = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    failed_tokens.append(tokens[idx])
                    print(f"❌ Failed to send to token {tokens[idx][:20]}...: {resp.exception}")

            print(f"✅ Multicast notification sent: {response.success_count} succeeded, {response.failure_count} failed")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "failed_tokens": failed_tokens
            }

        except Exception as e:
            print(f"❌ Error sending multicast FCM notification: {str(e)}")
            return {"success_count": 0, "failure_count": len(tokens), "failed_tokens": tokens}

    def send_data_message(
        self,
        token: str,
        data: Dict[str, str]
    ) -> bool:
        try:
            message = messaging.Message(
                data=data,
                token=token,
                android=messaging.AndroidConfig(
                    priority='high'
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(content_available=True)
                    )
                )
            )

            response = messaging.send(message)
            print(f"✅ Successfully sent FCM data message: {response}")
            return True

        except Exception as e:
            print(f"❌ Error sending FCM data message: {str(e)}")
            return False
