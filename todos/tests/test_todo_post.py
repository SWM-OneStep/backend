from datetime import timedelta

import pytest
from django.urls import reverse

from todos.models import Todo

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
def test_create_todo_success(
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
    order,
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "date": date,
        "due_time": None,
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert "id" in response.data


@pytest.mark.django_db
def test_create_todo_invalid_order(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        order=order(1),
    )
    data = {
        "user_id": create_user.id,
        "date": date + timedelta(days=2),
        "due_time": None,
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_todo_invalid_category_id(
    create_user, authenticated_client, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "date": date,
        "due_time": None,
        "content": content,
        "category_id": 999,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
