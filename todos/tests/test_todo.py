import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from todos.models import Todo

User = get_user_model()
client = APIClient()

"""
======================================
# Todo Post checklist #
- correct test
- order validation
- start_date and end_date validation
- category_id validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_create_todo_success(
    authenticated_client, create_category, create_user
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": "2024-08-01",
        "end_date": "2024-08-02",
        "content": "Test Todo",
        "category_id": create_category.id,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert "id" in response.data


@pytest.mark.django_db
def test_create_todo_invalid_order(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    data = {
        "user_id": create_user.id,
        "start_date": "2024-08-01",
        "end_date": "2024-08-02",
        "content": "Test Todo",
        "category_id": create_category.id,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
    assert (
        response.data["non_field_errors"][0] == "Order is invalid"
    )  # Adjust the assertion based on the actual error message


@pytest.mark.django_db
def test_create_todo_invalid_start_date(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": "2024-08-02",
        "end_date": "2024-08-01",
        "content": "Test Todo",
        "category_id": create_category.id,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_todo_valid_start_date(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": "2024-08-02",
        "content": "Test Todo",
        "category_id": create_category.id,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_todo_invalid_category_id(create_user, authenticated_client):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "start_date": "2024-08-01",
        "end_date": "2024-08-02",
        "content": "Test Todo",
        "category_id": 999,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_todo_invalid_user_id(authenticated_client, create_category):
    url = reverse("todos")
    data = {
        "user_id": 999,
        "start_date": "2024-08-01",
        "end_date": "2024-08-02",
        "content": "Test Todo",
        "category_id": create_category.id,
        "order": "0|hzzzzz:",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


"""
======================================
# Todo Get checklist #
- correct test
- right order
- get between start_date and end_date
======================================
"""


@pytest.mark.django_db
def test_get_todos(create_user, create_category, authenticated_client):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 1",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i00000:",
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_todos_ordering(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 1",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i00000:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 3",
        category_id=create_category,
        order="0|a0000a:",
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200

    assert response.data[0]["order"] == "0|a0000a:"
    assert response.data[1]["order"] == "0|hzzzzz:"
    assert response.data[2]["order"] == "0|i00000:"


@pytest.mark.django_db
def test_get_todos_between_dates(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-02",
        end_date="2024-08-04",
        content="Test Todo 1",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-04",
        end_date="2024-08-06",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i0000i:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-06",
        end_date="2024-08-08",
        content="Test Todo 3",
        category_id=create_category,
        order="0|i00000:",
    )
    response = authenticated_client.get(
        url,
        {
            "user_id": create_user.id,
            "start_date": "2024-08-03",
            "end_date": "2024-08-06",
        },
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_todos_between_dates2(
    create_user, create_category, authenticated_client
):
    url = reverse("todos")
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-02",
        end_date="2024-08-04",
        content="Test Todo 1",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-04",
        end_date="2024-08-06",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i0000i:",
    )
    Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-07",
        end_date="2024-08-08",
        content="Test Todo 3",
        category_id=create_category,
        order="0|i00000:",
    )
    response = authenticated_client.get(
        url,
        {
            "user_id": create_user.id,
            "start_date": "2024-08-03",
            "end_date": "2024-08-06",
        },
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 2


"""
======================================
# Todo Patch checklist #
- correct test
- order validation
- start_date and end_date validation
- category_id validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_update_todo_success(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    url = reverse("todos")  # URL name for the TodoView patch method
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": "2024-08-01",
        "end_date": "2024-08-03",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated Todo"
    assert response.data["end_date"] == "2024-08-03"


@pytest.mark.django_db
def test_update_todo_success_order(
    create_user, create_category, authenticated_client
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i00000:",
    )
    url = reverse("todos")  # URL name for the TodoView patch method
    data = {
        "todo_id": todo.id,
        "order": {
            "prev_id": todo2.id,
            "next_id": None,
            "updated_order": "0|j0000i:",
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["order"] == "0|j0000i:"


def test_update_todo_invalid_order(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    todo2 = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo 2",
        category_id=create_category,
        order="0|i0000h:",
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": "2024-08-01",
        "end_date": "2024-08-03",
        "order": {
            "prev_id": None,
            "next_id": todo2.id,
            "updated_order": "0|i0000z:",
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_start_date(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": "2024-08-02",
        "end_date": "2024-08-01",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
    assert (
        response.data["non_field_errors"][0]
        == "Start date should be less than end date"
    )  # Adjust the assertion based on the actual error message


@pytest.mark.django_db
def test_update_todo_invalid_category_id(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": "2024-08-01",
        "end_date": "2024-08-03",
        "category_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_todo_invalid_user_id(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
    )
    url = reverse("todos")
    data = {
        "todo_id": todo.id,
        "content": "Updated Todo",
        "start_date": "2024-08-01",
        "end_date": "2024-08-03",
        "user_id": 999,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


"""
======================================
# Todo Delete checklist #
- correct test
- todo_id validation
======================================
"""


@pytest.mark.django_db
def test_delete_todo_success(
    authenticated_client, create_category, create_user
):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-02",
        content="Test Todo",
        category_id=create_category,
        order="0|hzzzzz:",
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
