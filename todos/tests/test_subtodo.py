import pytest
from django.urls import reverse

from todos.models import SubTodo

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
def test_create_subtodo_success(
    create_todo, authenticated_client, content, date, order
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": create_todo.id,
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    response_data = response.data[0]  # 리스트의 첫 번째 항목 접근
    assert "id" in response_data


@pytest.mark.django_db
def test_create_subtodo_invalid_order(
    create_todo, authenticated_client, content, date, order
):
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": create_todo.id,
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_subtodo_invalid_todo_id(
    authenticated_client, content, date, order
):
    url = reverse("subtodos")
    data = [
        {
            "content": content,
            "date": date,
            "todo": 999,  # Invalid todo id
            "order": order(0),
            "is_completed": False,
        }
    ]
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


"""
======================================
# Todo Get checklist #
- correct test
- right order
- get between start_date and end_date (later)
======================================
"""


@pytest.mark.django_db
def test_get_subtodos(create_todo, authenticated_client, content, date, order):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(1),
        is_completed=False,
    )
    response = authenticated_client.get(
        url, {"todo_id": create_todo.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_subtodos_ordering(
    create_todo, authenticated_client, content, date, order
):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(2),
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(1),
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    response = authenticated_client.get(
        url, {"todo_id": create_todo.id}, format="json"
    )
    assert response.status_code == 200
    assert response.data[0]["order"] == order(0)
    assert response.data[1]["order"] == order(1)
    assert response.data[2]["order"] == order(2)


@pytest.mark.django_db
def test_get_subtodos_between_dates(
    create_todo, authenticated_client, content, date, order
):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content=content,
        date="2024-08-02",
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date="2024-08-04",
        todo=create_todo,
        order=order(1),
        is_completed=False,
    )
    SubTodo.objects.create(
        content=content,
        date="2024-08-06",
        todo=create_todo,
        order=order(2),
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
    create_todo, authenticated_client, content, date, order
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
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
def test_update_subtodo_invalid_order(
    create_todo, authenticated_client, content, date, order
):
    subtodo = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(0),
        is_completed=False,
    )
    subtodo2 = SubTodo.objects.create(
        content=content,
        date=date,
        todo=create_todo,
        order=order(1),
        is_completed=False,
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "order": {
            "prev_id": None,
            "next_id": subtodo2.id,
            "updated_order": order(2),
        },
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_subtodo_invalid_todo_id(
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
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "todo": 999,  # Invalid todo id
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
