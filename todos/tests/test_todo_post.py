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
    authenticated_client, create_category, create_user, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": date,
        "end_date": date + timedelta(days=1),
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
        start_date=date,
        end_date=date + timedelta(days=1),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    data = {
        "user_id": create_user.id,
        "start_date": date + timedelta(days=2),
        "end_date": date + timedelta(days=3),
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
    assert response.data["non_field_errors"][0] == "Order is invalid"


@pytest.mark.django_db
def test_create_todo_invalid_start_date(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": date + timedelta(days=2),
        "end_date": date + timedelta(days=1),
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_todo_valid_start_date(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": date + timedelta(days=2),
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_todo_invalid_category_id(
    create_user, authenticated_client, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=2),
        "content": content,
        "category_id": 999,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_todo_invalid_user_id(
    authenticated_client, create_category, date, content, order
):
    url = reverse("todos")
    data = {
        "user_id": 999,
        "start_date": date + timedelta(days=1),
        "end_date": date + timedelta(days=2),
        "content": content,
        "category_id": create_category.id,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
