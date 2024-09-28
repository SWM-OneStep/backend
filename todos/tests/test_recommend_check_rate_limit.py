import time
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status


@patch("todos.views.client.chat.completions.create")
def test_rate_limit_exceeded(mock_llm, authenticated_client, create_todo, llm):
    mock_llm.return_value = llm
    url = reverse("recommend")
    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.data["error"] == "Rate limit exceeded"


@patch("todos.views.client.chat.completions.create")
def test_rate_limit_passed(mock_llm, authenticated_client, create_todo, llm):
    url = reverse("recommend")
    mock_llm.return_value = llm

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK

    time.sleep(10)

    response = authenticated_client.get(url, {"todo_id": create_todo.id})
    assert response.status_code == status.HTTP_200_OK
