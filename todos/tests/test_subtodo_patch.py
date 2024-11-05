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
    create_todo, authenticated_client, content, date, rank
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[0],
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
def test_update_subtodo_success_top_rank(
    create_todo, authenticated_client, content, date, rank
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[1],
    )
    subtodo2 = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[1],
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo2.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "patch_rank": {
            "prev_id": None,
            "next_id": subtodo.id,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated SubTodo"
    assert response.data["rank"] < subtodo.rank


@pytest.mark.django_db
def test_update_subtodo_success_bottom_rank(
    create_todo, authenticated_client, content, date, rank
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[0],
    )
    subtodo2 = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[1],
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "patch_rank": {
            "prev_id": subtodo2.id,
            "next_id": None,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated SubTodo"
    assert response.data["rank"] > subtodo2.rank


@pytest.mark.django_db
def test_update_subtodo_success_between_rank(
    create_todo, authenticated_client, content, date, rank
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[0],
    )
    subtodo2 = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[1],
    )
    subtodo3 = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[2],
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "patch_rank": {
            "prev_id": subtodo2.id,
            "next_id": subtodo3.id,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated SubTodo"
    assert response.data["rank"] < subtodo3.rank
    assert response.data["rank"] > subtodo2.rank


@pytest.mark.django_db
def test_update_subtodo_invalid_todo_id(
    create_todo, authenticated_client, content, date, rank
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo_id=create_todo,
        is_completed=False,
        rank=rank[0],
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "todo_id": 999,  # Invalid todo id
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
