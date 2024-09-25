from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from fcm_django.models import FCMDevice
from rest_framework import status
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
            "is_subscribed": False,
        }


@pytest.mark.django_db
def test_update_user_is_subscribed(
    create_user, authenticated_client, content, order, color
):
    url = reverse("user")  # URL name for the categoryView patch method
    data = {
        "is_subscribed": True,
    }
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == 200
    assert response.data["is_subscribed"]


@pytest.mark.django_db
def test_google_login(invalid_token):
    client = APIClient()
    response = client.post(reverse("google_login"), data=invalid_token)
    assert response.status_code == 400


@pytest.mark.django_db
def test_google_login_missing_device_token():
    client = APIClient()
    response = client.post(reverse("google_login"))
    assert response.status_code == 400


@pytest.mark.django_db
class TestGoogleLogin:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @patch("accounts.views.id_token.verify_oauth2_token")
    @patch("accounts.models.send_welcome_email")
    def test_google_login_new_user(
        self, mock_send_welcome_email, mock_verify_oauth2_token, api_client
    ):
        # Mock the token verification response
        mock_verify_oauth2_token.return_value = {
            "iss": "accounts.google.com",
            "email": "testuser@example.com",
        }

        # Define the URL for the GoogleLogin view
        url = reverse("google_login")

        # Create a mock request
        data = {"token": "mock_token", "device_token": "mock_device_token"}

        # Call the view
        response = api_client.post(url, data, format="json")

        # Check that the user was created
        user = User.objects.get(username="testuser@example.com")
        assert user is not None

        # Check that the device was created
        device = FCMDevice.objects.get(
            user_id=user.id, registration_id="mock_device_token"
        )
        assert device is not None

        # Check that the email was sent
        mock_send_welcome_email.assert_called_once_with(
            user.username,
            user.username,
        )

        # Check the response status
        assert response.status_code == status.HTTP_200_OK
        assert "refresh" in response.data
        assert "access" in response.data
