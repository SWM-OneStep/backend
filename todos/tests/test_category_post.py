import pytest
from django.urls import reverse

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
    create_user, authenticated_client, content, color
):
    url = reverse("category")
    data = {
        "user_id": create_user.id,
        "title": content,
        "color": color,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == 201
