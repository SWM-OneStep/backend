import pytest
from django.urls import reverse

"""
======================================
# SubTodo Post checklist #
- correct test
- order validation
- date validation (later)
- todo_id validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_create_subtodo_success(
    create_todo, authenticated_client, content, date
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "due_time": None,
            "todo_id": create_todo.id,
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data[0]["content"] == content


@pytest.mark.django_db
def test_create_subtodo_success_many(
    create_todo, authenticated_client, content, date
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "due_time": None,
            "todo_id": create_todo.id,
            "is_completed": False,
        },
        {
            "content": content + "2",
            "date": date,
            "due_time": None,
            "todo_id": create_todo.id,
            "is_completed": False,
        },
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data[0]["content"] == content
    assert response.data[1]["content"] == content + "2"
    assert response.data[0]["rank"] < response.data[1]["rank"]


@pytest.mark.django_db
def test_create_subtodo_invalid_todo_id(authenticated_client, content, date):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "due_time": None,
            "todo_id": 999,  # Invalid todo id
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
