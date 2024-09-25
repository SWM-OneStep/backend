import firebase_admin
import os
from firebase_admin import credentials, messaging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep_be.settings')
from django.conf import settings
from dataclasses import dataclass
from fcm_django.models import FCMDevice



@dataclass
class PushNotificationStatus:
    status: str


PUSH_NOTIFICATION_SUCCESS = PushNotificationStatus("success")
PUSH_NOTIFICATION_ERROR = PushNotificationStatus("error")


def send_push_notification(token, title, body):
    device = FCMDevice.objects.filter(registration_id=token).first()
    try:
        device.send_message(
            messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
            )
        )
    except Exception as e:
        print("e", e)
        return PUSH_NOTIFICATION_ERROR
    return PUSH_NOTIFICATION_SUCCESS