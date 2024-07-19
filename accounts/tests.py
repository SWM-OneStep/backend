from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest

User = get_user_model()


@pytest.fixture(scope='module')
def invalid_token():
    response = {
        "token": "token",
        "deviceToken": "device_token"
    }
    return response


def test_google_login(invalid_token):
    client = APIClient()
    response = client.post(reverse('google_login'), data=invalid_token)
    assert response.status_code == 400
