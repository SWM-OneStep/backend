import pytest
from django.urls import reverse

from todos.models import Category

"""
======================================
# category Get checklist #
- correct test
- right order
======================================
"""


@pytest.mark.django_db
def test_get_category(create_user, authenticated_client, content, color):
    url = reverse("category")
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
    )
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_category_ordering(
    create_user, authenticated_client, content, color
):
    url = reverse("category")
    Category.objects.create(
        user_id=create_user,
        title="1",
        color=color,
    )
    Category.objects.create(
        user_id=create_user,
        title="2",
        color=color,
    )
    Category.objects.create(
        user_id=create_user,
        title="3",
        color=color,
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert response.data[0]["title"] == "1"
    assert response.data[1]["title"] == "2"
    assert response.data[2]["title"] == "3"
