import datetime
from datetime import timedelta

import pytest
from django.urls import reverse

from Lexorank.src.lexo_rank import LexoRank
from todos.models import SubTodo, Todo

"""
======================================
# Todo Patch checklist #
- correct test
- order validation
- date validation (later)
- todo_id validation
- user_id validation
- if update todo date then subtodo date also updated 
======================================
"""


@pytest.mark.django_db
def test_update_todo_success(
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
    due_time,
    rank,
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
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "date": date + timedelta(days=1),
        "due_time": due_time,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated Todo"
    assert response.data["date"] == str(data["date"])


@pytest.mark.django_db
def test_update_todo_success_bottom_order(
    create_user, create_category, authenticated_client, date, content, rank
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[0],
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[1],
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "patch_rank": {
            "prev_id": todo2.id,
            "next_id": None,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["rank"] > todo2.rank


@pytest.mark.django_db
def test_update_todo_success_top_order(
    create_user, create_category, authenticated_client, date, content, rank
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[0],
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[1],
    )
    url = reverse("todos")
    data = {
        "todo_id": todo2.id,
        "patch_rank": {
            "prev_id": None,
            "next_id": todo.id,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert LexoRank.parse(response.data["rank"]) < LexoRank.parse(todo.rank)


@pytest.mark.django_db
def test_update_todo_success_None_order(
    create_user, create_category, authenticated_client, date, content, rank
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[0],
    )
    before_rank = todo.rank
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "patch_rank": {
            "prev_id": None,
            "next_id": None,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["rank"] == before_rank


@pytest.mark.django_db
def test_update_todo_success_between_order(
    create_user, create_category, authenticated_client, date, content, rank
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[0],
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[1],
    )
    todo3 = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
        rank=rank[2],
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "patch_rank": {
            "prev_id": todo2.id,
            "next_id": todo3.id,
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["rank"] > todo2.rank
    assert response.data["rank"] < todo3.rank


@pytest.mark.django_db
def test_update_todo_invalid_category_id(
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "category_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_user_id(
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "user_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_date_with_subtodo(
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
):
    todo = Todo.objects.create(
        user_id=create_user,
        date=date,
        due_time=None,
        content=content,
        category_id=create_category,
    )
    subtodo = SubTodo.objects.create(
        todo_id=todo,
        content="Test subtodo",
        date="2024-08-01",
        due_time=None,
        is_completed=False,
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "date": "2024-11-11",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated Todo"
    assert response.data["date"] == "2024-11-11"
    subtodo.refresh_from_db()
    assert subtodo.date == datetime.date(2024, 11, 11)
