import pytest
from django.urls import reverse

from todos.models import SubTodo

"""
======================================
# Todo Delete checklist #
- correct test
- todo_id validation
======================================
"""


@pytest.mark.django_db
def test_delete_subtodo_success(
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
    data = {"subtodo_id": subtodo.id}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 200

    # Check if the subtodo is soft deleted
    subtodo.refresh_from_db()
    assert subtodo.deleted_at is not None
    assert not SubTodo.objects.filter(
        id=subtodo.id, deleted_at__isnull=True
    ).exists()


@pytest.mark.django_db
def test_delete_subtodo_invalid_id(authenticated_client, content, date, order):
    url = reverse("subtodos")
    data = {
        "subtodo_id": 999  # Invalid subtodo id
    }
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 400
