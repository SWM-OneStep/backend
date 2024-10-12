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
def test_get_todos(
    create_user,
    date,
    content,
    create_category,
    authenticated_client,
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_todos_ordering(
    create_user, create_category, authenticated_client, date, content
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    Todo.objects.create(
        user_id=create_user,
        date=date + timedelta(days=1),
        due_time=None,
        content=content,
        category_id=create_category,
    )
    Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
