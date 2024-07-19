from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.exceptions import PermissionDenied
import pytest
import logging


client = APIClient()
User = get_user_model()


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword'
    )
    return user


@override_settings(REST_FRAMEWORK={'DEFAULT_PERMISSION_CLASSES': []})
@pytest.mark.django_db
def test_user_info(create_user):
    with patch('accounts.views.UserRetrieveView.permission_classes', new=[]):
        url = reverse('user', args=[1])
        response = client.get(url)
        assert response.status_code == 200
        assert response.data == {
            'id': 1,
            'email': create_user.email,
            'username': create_user.username,
            'social_provider': 'GOOGLE',
        }


@pytest.mark.django_db
def test_user_info_without_permission(create_user):
    url = reverse('user', args=[1])
    client.get(url)
    assert pytest.raises(PermissionDenied)
