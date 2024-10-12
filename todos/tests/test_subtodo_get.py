import pytest
from django.urls import reverse

from todos.models import SubTodo

"""
======================================
# Todo Get checklist #
- correct test
- right order
- get between start_date and end_date (later)
======================================
"""


@pytest.mark.django_db
def test_get_subtodos(create_todo, authenticated_client, content, date):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
    )
    response = authenticated_client.get(
        url, {"todo_id": create_todo.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_subtodos_ordering(
    create_todo, authenticated_client, content, date
):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content="1",
        date=date,
        todo_id=create_todo,
        is_completed=False,
    )
    SubTodo.objects.create(
        content="2",
        date=date,
        todo_id=create_todo,
        is_completed=False,
    )
    SubTodo.objects.create(
        content="3",
        date=date,
        todo_id=create_todo,
        is_completed=False,
    )
    response = authenticated_client.get(
        url, {"todo_id": create_todo.id}, format="json"
    )
    assert response.status_code == 200
    assert response.data[0]["content"] == "1"
    assert response.data[1]["content"] == "2"
    assert response.data[2]["content"] == "3"


@pytest.mark.django_db
def test_get_subtodos_between_dates(
    create_todo, authenticated_client, content
):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content=content,
        date="2024-08-02",
        todo_id=create_todo,
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date="2024-08-04",
        todo_id=create_todo,
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date="2024-08-06",
        todo_id=create_todo,
        is_completed=False,
    )
    response = authenticated_client.get(
        url,
        {
            "todo_id": create_todo.id,
            "start_date": "2024-08-03",
            "end_date": "2024-08-06",
        },
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 3
