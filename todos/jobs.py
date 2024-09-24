import firebase_admin
import os
from firebase_admin import credentials, messaging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep_be.settings')
from django.conf import settings
from fcm_django.models import FCMDevice
from django.db.models import Prefetch
from todos.models import Todo


firebase_info = eval(settings.SECRETS.get("FIREBASE"))
cred = credentials.Certificate(firebase_info)
firebase_admin.initialize_app(cred)


MORNING_ALARM_TITLE = "오늘의 할 일을 확인해보세요"
AFTERNOON_ALARM_TITLE = "지금 할 일을 확인해보세요"
EVENING_ALARM_TITLE = "오늘의 남은 할 일을 확인해보세요"


def send_morning_alarm():
    send_day_alarm(MORNING_ALARM_TITLE)


def send_afternoon_alarm():
    send_day_alarm(AFTERNOON_ALARM_TITLE)


def send_evening_alarm():
    send_day_alarm(EVENING_ALARM_TITLE)


def send_day_alarm(alarm_title):
    users_prefetch = Prefetch('user__todo_set', queryset=Todo.objects.filter(is_completed=False))
    devices = FCMDevice.objects.all().select_related('user').prefetch_related(users_prefetch)
    try:
        for device in devices:
            todos_queryset = device.user.todo_set.filter(is_completed=False).values_list("content", flat=True)
            todos_list = "\n".join(todos_queryset)
            device.send_message(
                messaging.Message(
                    notification=messaging.Notification(
                        title=alarm_title,
                        body=todos_list,
                    ),
                )
            )
    except Exception:
        pass
    
