import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from todos.models import Category, SubTodo, Todo, User

client = APIClient()


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    return user


@pytest.fixture
def create_category(db, create_user):
    category = Category.objects.create(
        user_id=create_user,
        title="Test Category",
        color="#FFFFFF",
        order="0|hzzzzz:",
    )
    return category


@pytest.fixture
def create_todo(db, create_user, create_category):
    todo = Todo.objects.create(
        user_id=create_user,
        start_date="2024-08-01",
        end_date="2024-08-30",
        category_id=create_category,
        content="Test Todo",
        order="0|hzzzzz:",
        is_completed=False,
    )
    return todo


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
def test_create_subtodo_success(create_todo):
    url = reverse("subtodos")
    data = [
        {
            "content": "Test SubTodo",
            "date": "2024-08-02",
            "todo": create_todo.id,
            "order": "0|hzzzzz:",
            "is_completed": False,
        }
    ]
    response = client.post(url, data, format="json")
    assert response.status_code == 201
    response_data = response.data[0]  # 리스트의 첫 번째 항목 접근
    assert "id" in response_data


@pytest.mark.django_db
def test_create_subtodo_invalid_order(create_todo):
    SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    url = reverse("subtodos")
    data = [
        {
            "content": "Test SubTodo2",
            "date": "2024-08-01",
            "todo": create_todo.id,
            "order": "0|hzzzzz:",
            "is_completed": False,
        }
    ]
    response = client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_subtodo_invalid_todo_id():
    url = reverse("subtodos")
    data = [
        {
            "content": "Test SubTodo",
            "date": "2024-08-01",
            "todo": 999,  # Invalid todo id
            "order": "0|hzzzzz:",
            "is_completed": False,
        }
    ]
    response = client.post(url, data, format="json")
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
def test_get_subtodos(create_todo):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content="Test SubTodo 1",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    SubTodo.objects.create(
        content="Test SubTodo 2",
        date="2024-08-01",
        todo=create_todo,
        order="0|i00000:",
        is_completed=False,
    )
    response = client.get(url, {"todo_id": create_todo.id}, format="json")
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_subtodos_ordering(create_todo):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content="Test SubTodo 1",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    SubTodo.objects.create(
        content="Test SubTodo 2",
        date="2024-08-01",
        todo=create_todo,
        order="0|i00000:",
        is_completed=False,
    )
    SubTodo.objects.create(
        content="Test SubTodo 3",
        date="2024-08-01",
        todo=create_todo,
        order="0|00000a:",
        is_completed=False,
    )
    response = client.get(url, {"todo_id": create_todo.id}, format="json")
    assert response.status_code == 200
    assert response.data[0]["order"] == "0|00000a:"
    assert response.data[1]["order"] == "0|hzzzzz:"
    assert response.data[2]["order"] == "0|i00000:"


@pytest.mark.django_db
def test_get_subtodos_between_dates(create_todo):
    url = reverse("subtodos")
    SubTodo.objects.create(
        content="Test SubTodo 1",
        date="2024-08-02",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    SubTodo.objects.create(
        content="Test SubTodo 2",
        date="2024-08-04",
        todo=create_todo,
        order="0|i0000i:",
        is_completed=False,
    )
    SubTodo.objects.create(
        content="Test SubTodo 3",
        date="2024-08-06",
        todo=create_todo,
        order="0|i00000:",
        is_completed=False,
    )
    response = client.get(
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
def test_update_subtodo_success(create_todo):
    subtodo = SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    url = reverse("subtodos")  # URL name for the SubTodoView patch method
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
    }
    response = client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["content"] == "Updated SubTodo"
    assert response.data["date"] == "2024-08-03"


@pytest.mark.django_db
def test_update_subtodo_invalid_order(create_todo):
    subtodo = SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    subtodo2 = SubTodo.objects.create(
        content="Test SubTodo 2",
        date="2024-08-01",
        todo=create_todo,
        order="0|i00000:",
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
            "updated_order": "0|ii0000:",
        },
    }
    response = client.patch(url, data, format="json")
    assert response.status_code == 400
    assert response.data["error"] == "Invalid order"


@pytest.mark.django_db
def test_update_subtodo_invalid_todo_id(create_todo):
    subtodo = SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    url = reverse("subtodos")
    data = {
        "subtodo_id": subtodo.id,
        "content": "Updated SubTodo",
        "date": "2024-08-03",
        "todo": 999,  # Invalid todo id
    }
    response = client.patch(url, data, format="json")
    assert response.status_code == 400


"""
======================================
# Todo Delete checklist #
- correct test
- todo_id validation
======================================
"""


@pytest.mark.django_db
def test_delete_subtodo_success(create_todo):
    subtodo = SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    url = reverse("subtodos")
    data = {"subtodo_id": subtodo.id}
    response = client.delete(url, data, format="json")
    assert response.status_code == 200

    # Check if the subtodo is soft deleted
    subtodo.refresh_from_db()
    assert subtodo.deleted_at is not None
    assert not SubTodo.objects.filter(
        id=subtodo.id, deleted_at__isnull=True
    ).exists()


@pytest.mark.django_db
def test_delete_subtodo_invalid_id():
    url = reverse("subtodos")
    data = {
        "subtodo_id": 999  # Invalid subtodo id
    }
    response = client.delete(url, data, format="json")
    assert response.status_code == 400
