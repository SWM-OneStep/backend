from fcm_django.models import FCMDevice
import firebase_admin
import os
from firebase_admin import credentials, messaging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep_be.settings')
from django.conf import settings
from fcm_django.models import FCMDevice
from todos.firebase_messaging import send_push_notification


FCM_ALARM_PATH_TODO = "/todos/todo"
FCM_ALARM_PATH_SUBTODO = "/todos/subtodo"
FCM_ALARM_PATH_CATEGORY = "/todos/category"

FCM_ALARM_PATHS = [FCM_ALARM_PATH_TODO, FCM_ALARM_PATH_SUBTODO, FCM_ALARM_PATH_CATEGORY] 
FCM_ALARM_METHODS = [
    "POST", "PATCH", "DELETE"
]


class FCMAlarmMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def startswith_fcm_alarm_paths(self, path):
        for p in FCM_ALARM_PATHS:
            if path.startswith(p):
                return True
        return False

    def __call__(self, request):

        if request.method in FCM_ALARM_METHODS and self.startswith_fcm_alarm_paths(request.path):
            fcm_token = request.auth.token
            other_device = FCMDevice.objects.filter(user=request.user).exclude(registration_id=fcm_token)

            if other_device.exists():
                device_id = other_device.first().registration_id

                if request.path.startsWith(FCM_ALARM_PATH_TODO):
                    send_push_notification(device_id, "Todo", "")
                elif request.path.startsWith(FCM_ALARM_PATH_SUBTODO):
                    send_push_notification(device_id, "Subtodo", "")
                elif request.path.startsWith(FCM_ALARM_PATH_CATEGORY):
                    send_push_notification(device_id, "Category", "")
