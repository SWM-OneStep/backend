from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient, force_authenticate
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.exceptions import PermissionDenied
from accounts.views import UserRetrieveView
import pytest
import logging



client = APIClient()
User = get_user_model()
factory = APIRequestFactory()
view = UserRetrieveView.as_view()


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


@pytest.mark.django_db
def test_user_info_without_permission(create_user):
    with pytest.raises(User.DoesNotExist):
        request = factory.get(reverse('user'))
        view(request)
