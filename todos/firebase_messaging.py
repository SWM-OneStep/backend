import firebase_admin
import os
from firebase_admin import credentials, messaging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep_be.settings')
from django.conf import settings
from dataclasses import dataclass


firebase_info = eval(settings.SECRETS.get("FIREBASE"))
cred = credentials.Certificate(firebase_info)
firebase_admin.initialize_app(cred)


@dataclass
class PushNotificationStatus:
    status: str


PUSH_NOTIFICATION_SUCCESS = PushNotificationStatus("success")
PUSH_NOTIFICATION_ERROR = PushNotificationStatus("error")


def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    try:
        messaging.send(message)
    except Exception as e:
        # sentry capture exception
        return PUSH_NOTIFICATION_ERROR
    return PUSH_NOTIFICATION_SUCCESS