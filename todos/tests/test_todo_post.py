import pytest
from django.urls import reverse

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
    authenticated_client,
    create_category,
    create_user,
    date,
    content,
):
    url = reverse("todos")
    data = {
        "date": date,
        "due_time": None,
        "content": content,
        "category_id": create_category.id,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert "id" in response.data
    assert response.data.rank == "mzzzz"


@pytest.mark.django_db
def test_create_todo_invalid_category_id(
    create_user, authenticated_client, date, content
):
    url = reverse("todos")
    data = {
        "user_id": create_user.id,
        "date": date,
        "due_time": None,
        "content": content,
        "category_id": 999,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
