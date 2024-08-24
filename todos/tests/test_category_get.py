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
def test_get_category(
    create_user, authenticated_client, content, order, color
):
    url = reverse("category")
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(1),
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_category_ordering(
    create_user, authenticated_client, content, order, color
):
    url = reverse("category")
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(2),
    )
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(1),
    )
    Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    response = authenticated_client.get(
        url, {"user_id": create_user.id}, format="json"
    )
    assert response.status_code == 200
    assert response.data[0]["order"] == order(0)
    assert response.data[1]["order"] == order(1)
    assert response.data[2]["order"] == order(2)
