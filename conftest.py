# This file is for Pytest Configuration
# This file is used to define fixtures that can be used in multiple test files

import pytest
from faker import Faker
from rest_framework.test import APIClient

from todos.models import Category, SubTodo, Todo, User

client = APIClient()

fake = Faker()


@pytest.fixture(scope="module")
def invalid_token():
    response = {"token": "token", "deviceToken": "device_token"}
    return response


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    return user


@pytest.fixture
def authenticated_client(create_user):
    client.force_authenticate(user=create_user)
    yield client
    client.force_authenticate(user=None)  # logout


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


@pytest.fixture
def create_subtodo(db, create_user, create_todo):
    subtodo = SubTodo.objects.create(
        content="Test SubTodo",
        date="2024-08-01",
        todo=create_todo,
        order="0|hzzzzz:",
        is_completed=False,
    )
    return subtodo


@pytest.fixture
def date():
    return fake.date_this_year()


@pytest.fixture
def content():
    return fake.sentence(nb_words=6)
