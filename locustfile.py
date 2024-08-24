from locust import HttpUser, task
from django.conf import settings
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onestep_be.setting.dev")

class TestTodos(HttpUser):

    @task
    def get_android_client_id(self) -> None:
        self.client.get("/auth/android")

