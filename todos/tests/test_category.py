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


@pytest.mark.django_db
def test_create_category_invalid_user_id(
    authenticated_client, content, order, color
):
    url = reverse("category")
    data = {
        "user_id": 999,
        "title": content,
        "color": color,
        "order": order(0),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 400


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
