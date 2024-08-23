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
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_todos_ordering(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(2),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=1),
        end_date=date + timedelta(days=2),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200

    assert response.data[0]["order"] == order(0)
    assert response.data[1]["order"] == order(1)
    assert response.data[2]["order"] == order(2)


@pytest.mark.django_db
def test_get_todos_between_dates(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=2),
        end_date=date + timedelta(days=4),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=4),
        end_date=date + timedelta(days=6),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=6),
        end_date=date + timedelta(days=8),
        content=content,
        category_id=create_category,
        order=order(2),
    )
    response = authenticated_client.get(
        url,
        {
            "user_id": create_user.id,
            "start_date": date + timedelta(days=3),
            "end_date": date + timedelta(days=6),
        },
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_todos_between_dates2(
    create_user, create_category, authenticated_client, date, content, order
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=2),
        end_date=date + timedelta(days=4),
        content=content,
        category_id=create_category,
        order=order(0),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=4),
        end_date=date + timedelta(days=6),
        content=content,
        category_id=create_category,
        order=order(1),
    )
    Todo.objects.create(
        user_id=create_user,
        start_date=date + timedelta(days=7),
        end_date=date + timedelta(days=8),
        content=content,
        category_id=create_category,
        order=order(2),
    )
    response = authenticated_client.get(
        url,
        {
            "user_id": create_user.id,
            "start_date": date + timedelta(days=3),
            "end_date": date + timedelta(days=6),
        },
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 2
