from locust import HttpUser, task

class TestApi(HttpUser):

    @task
    def retrieve_todo(self):
        self.client.get("/todos/todo?user_id=1")
