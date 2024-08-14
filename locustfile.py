from locust import HttpUser, task
from django.conf import settings

class TestTodos(HttpUser):

    def on_start(self) -> None:
        test_db_info = settings.DATABASES.get("test")
        self.db_host = test_db_info.get("HOST")
        self.db_name = test_db_info.get("NAME")
        self.db_user = test_db_info.get("USER")
        self.db_password = test_db_info.get("PASSWORD")

    @task
    def retrieve_todo(self) -> None:
        self.client.get("/todos/todo?user_id=1")

    @task
    def create_todo(self) -> None:
        self.client.post("/todos/todo?user_id=1")

