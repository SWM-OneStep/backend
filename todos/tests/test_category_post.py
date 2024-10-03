import pytest
from django.urls import reverse

from todos.models import Category

"""
======================================
# Todo Post checklist #
- correct test
- order validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_create_category_success(
    create_user, authenticated_client, content, order, color
):
    url = reverse("category")
    data = {
        "user_id": create_user.id,
        "title": content,
        "color": color,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
    assert "id" in response.data


@pytest.mark.django_db
def test_create_category_invalid_order(
    create_user, authenticated_client, content, order, color
):
    url = reverse("category")
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    data = {
        "user_id": create_user.id,
        "title": content,
        "color": color,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400
