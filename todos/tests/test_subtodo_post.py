import pytest
from django.urls import reverse

from todos.models import SubTodo

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
    create_todo, authenticated_client, content, date, order
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": create_todo.id,
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    response_data = response.data[0]  # 리스트의 첫 번째 항목 접근
    assert "id" in response_data


@pytest.mark.django_db
def test_create_subtodo_invalid_order(
    create_todo, authenticated_client, content, date, order
):
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": create_todo.id,
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_subtodo_invalid_todo_id(
    authenticated_client, content, date, order
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": 999,  # Invalid todo id
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
