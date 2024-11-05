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
    authenticated_client, create_category, create_user, date, content, rank
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[0],
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
def test_delete_todo_invalid_id(authenticated_client):
    url = reverse("todos")
    data = {"todo_id": 999}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 400
