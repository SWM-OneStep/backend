from datetime import timedelta

import pytest
from django.urls import reverse

from todos.models import Todo

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
def test_update_todo_success(
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
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=3),
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated Todo"
    assert response.data["end_date"] == str(data["end_date"])


@pytest.mark.django_db
def test_update_todo_success_order(
    create_user, create_category, authenticated_client, date, content, order
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "order": {
            "prev_id": todo2.id,
            "next_id": None,
            "updated_order": order(2),
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["order"] == order(2)


@pytest.mark.django_db
def test_update_todo_invalid_order(
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
    todo2 = Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=3),
        "order": {
            "prev_id": None,
            "next_id": todo2.id,
            "updated_order": order(2),
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_start_date(
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
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": date + timedelta(days=2),
        "end_date": date + timedelta(days=1),
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_category_id(
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
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=3),
        "category_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_user_id(
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
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=3),
        "user_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
