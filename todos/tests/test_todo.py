from datetime import timedelta

import pytest
from django.urls import reverse

from todos.models import Todo


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
