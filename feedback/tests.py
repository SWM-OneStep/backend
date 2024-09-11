import pytest
from django.urls import reverse

"""
======================================
# category Get checklist #
- correct test
- invalid user_id
- invalid category
======================================
"""


@pytest.mark.django_db
def test_create_feedback_success(
    create_user, authenticated_client, title, category, content
):
    url = reverse("feedback")
    data = {
        "user_id": create_user.id,
        "title": title,
        "category": category,
        "description": content,
    }

    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_feedback_invalid_user_id(
    authenticated_client, title, category, content
):
    url = reverse("feedback")
    data = {
        "user_id": 999,
        "title": title,
        "category": category,
        "description": content,
    }

    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_feedback_invalid_category(
    create_user, authenticated_client, title, category, content
):
    url = reverse("feedback")
    data = {
        "user_id": create_user.id,
        "title": title,
        "category": "invalid Category",
        "description": content,
    }

    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
