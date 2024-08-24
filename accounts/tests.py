from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    force_authenticate,
)

from accounts.views import UserRetrieveView

User = get_user_model()
factory = APIRequestFactory()
view = UserRetrieveView.as_view()


@pytest.mark.django_db
def test_user_info(create_user):
    with patch("accounts.views.UserRetrieveView.permission_classes", new=[]):
        request = factory.get(reverse("user"))
        force_authenticate(request, user=create_user)
        response = view(request)
        assert response.status_code == 200
        assert response.data == {
            "id": 1,
            "email": create_user.email,
            "username": create_user.username,
            "social_provider": "GOOGLE",
        }


def test_google_login(invalid_token):
    client = APIClient()
    response = client.post(reverse("google_login"), data=invalid_token)
    assert response.status_code == 400
