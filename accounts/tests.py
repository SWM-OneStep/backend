from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient, force_authenticate
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from accounts.views import UserRetrieveView
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest



client = APIClient()
User = get_user_model()
factory = APIRequestFactory()
view = UserRetrieveView.as_view()


@pytest.fixture(scope='module')
def invalid_token():
    response = {
        "token": "token",
        "deviceToken": "device_token"
    }
    return response


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword'
    )
    return user


@pytest.mark.django_db
def test_user_info(create_user):
    with patch('accounts.views.UserRetrieveView.permission_classes', new=[]):
        request = factory.get(reverse('user'))
        force_authenticate(request, user=create_user)
        response = view(request)
        assert response.status_code == 200
        assert response.data == {
            'id': 1,
            'email': create_user.email,
            'username': create_user.username,
            'social_provider': 'GOOGLE',
        }


def test_google_login(invalid_token):
    client = APIClient()
    response = client.post(reverse('google_login'), data=invalid_token)
    assert response.status_code == 400
