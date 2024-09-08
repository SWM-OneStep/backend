import pytest
from django.urls import reverse

from todos.models import Category

"""
======================================
# category Delete checklist #
- correct test
- category_id validation
======================================
"""


@pytest.mark.django_db
def test_delete_category_success(
    create_user, authenticated_client, content, order, color
):
    category = Category.objects.create(
        user_id=create_user,
        title=content,
        color=color,
        order=order(0),
    )
    url = reverse("category")
    data = {"category_id": category.id}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 200

    # Check if the category is soft deleted
    category.refresh_from_db()
    assert Category.deleted_at is not None
    assert not Category.objects.filter(
        id=category.id, deleted_at__isnull=True
    ).exists()


@pytest.mark.django_db
def test_delete_category_invalid_id(
    authenticated_client, content, order, color
):
    url = reverse("category")
    data = {"category_id": 999}
    response = authenticated_client.delete(url, data, format="json")
    assert response.status_code == 400
