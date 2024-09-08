from datetime import timedelta

import pytest
from django.urls import reverse

from todos.models import Todo

"""
======================================
# Todo Delete checklist #
- correct test
- todo_id validation
======================================
"""


@pytest.mark.django_db
def test_delete_todo_success(
    authenticated_client, create_category, create_user, date, content, order
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    url = reverse("todos")
    data = {"todo_id": todo.id}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 200

    # Check if the todo is soft deleted
    todo.refresh_from_db()
    assert todo.deleted_at is not None
    assert not Todo.objects.filter(
        id=todo.id, deleted_at__isnull=True
    ).exists()


@pytest.mark.django_db
def test_delete_todo_invalid_id(authenticated_client, order):
    url = reverse("todos")
    data = {"todo_id": 999}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 400
