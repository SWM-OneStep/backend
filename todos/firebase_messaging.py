import firebase_admin
import os
from firebase_admin import credentials, messaging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep_be.settings')
from django.conf import settings
from dataclasses import dataclass
from fcm_django.models import FCMDevice
from django.contrib.auth import get_user_model


User = get_user_model()


@dataclass
class PushNotificationStatus:
    status: str


PUSH_NOTIFICATION_SUCCESS = PushNotificationStatus("success")
PUSH_NOTIFICATION_ERROR = PushNotificationStatus("error")


def send_push_notification_device(token, target_user, title, body):
    target_device = FCMDevice.objects.filter(user=target_user).exclude(registration_id=token)
    if target_device.exists():
        target_device = target_device.first()
        try:
            target_device.send_message(
                messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                )
            )
        except Exception:
            pass


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
    except Exception:
        return PUSH_NOTIFICATION_ERROR
    return PUSH_NOTIFICATION_SUCCESS