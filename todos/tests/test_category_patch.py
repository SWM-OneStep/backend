import pytest
from django.urls import reverse

from todos.models import Category

"""
======================================
# category Patch checklist #
- correct test
- order validation
- category_id validation
- user_id validation
======================================
"""


@pytest.mark.django_db
def test_update_category_success(
    create_user, authenticated_client, content, order, color
):
    category = Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    url = reverse("category")  # URL name for the categoryView patch method
    data = {
        "category_id": category.id,
        "title": "Updated category",
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["title"] == "Updated category"


@pytest.mark.django_db
def test_update_category_invalid_user_id(
    create_user, authenticated_client, content, order, color
):
    category = Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    url = reverse("category")
    data = {"category_id": category.id, "user_id": 999}
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 400
