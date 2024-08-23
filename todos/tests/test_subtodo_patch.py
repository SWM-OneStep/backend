import pytest
from django.urls import reverse

from todos.models import SubTodo

"""
======================================
# Todo Patch checklist #
- correct test
- order validation
- date validation (later)
- todo_id validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_update_subtodo_success(
    create_todo, authenticated_client, content, date, order
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    url = reverse("subtodos")  # URL name for the SubTodoView patch method
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated SubTodo"
    assert response.data["date"] == "2024-08-03"


@pytest.mark.django_db
def test_update_subtodo_invalid_order(
    create_todo, authenticated_client, content, date, order
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    subtodo2 = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(1),
        is_completed=False,
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "order": {
            "prev_id": None,
            "next_id": subtodo2.id,
            "updated_order": order(2),
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_subtodo_invalid_todo_id(
    create_todo, authenticated_client, content, date, order
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "todo": 999,  # Invalid todo id
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
