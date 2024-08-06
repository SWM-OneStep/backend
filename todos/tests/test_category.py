import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from todos.models import Category

User = get_user_model()
client = APIClient()

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword'
    )
    return user

'''
======================================
# Todo Post checklist #
- correct test
- order validation
- user_id validation
======================================
'''
@pytest.mark.django_db
def test_create_category_success(create_user):
    url = reverse('category') 
    data = {
        'user_id':create_user.id,
        'title':'Test Category',
        'color':'#FFFFFF',
        'order':'0|hzzzzz:'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert 'id' in response.data

@pytest.mark.django_db
def test_create_category_invalid_order(create_user):
    url = reverse('category')  
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|hzzzzz:'
    )
    data = {
        'user_id':create_user.id,
        'title':'Test Category2',
        'color':'#FFFFFF',
        'order':'0|hzzzzz:'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 400
    assert response.data['error'] == 'Invalid order'

@pytest.mark.django_db
def test_create_category_invalid_user_id(create_user):
    url = reverse('category')  
    data = {
        'user_id': 999,
        'title':'Test Category',
        'color':'#FFFFFF',
        'order':'0|hzzzzz:'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 400
'''
======================================
# category Get checklist #
- correct test
- right order
======================================
'''
@pytest.mark.django_db
def test_get_category(create_user):
    url = reverse('category')  
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|hzzzzz:'
    )
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|i00000:'
    )
    response = client.get(url, {'user_id': create_user.id}, format='json')
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_get_category_ordering(create_user):
    url = reverse('category')  
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|hzzzzz:'
    )
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|a0000a:'
    )
    Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|i00000:'
    )
    response = client.get(url, {'user_id': create_user.id}, format='json')
    assert response.status_code == 200
    print(response.data)
    assert response.data[0]['order'] == '0|a0000a:'
    assert response.data[1]['order'] == '0|hzzzzz:'
    assert response.data[2]['order'] == '0|i00000:'

'''
======================================
# category Patch checklist #
- correct test
- order validation
- category_id validation
- user_id validation
======================================
'''
@pytest.mark.django_db
def test_update_category_success(create_user):
    category = Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|i00000:'
    )
    url = reverse('category')  # URL name for the categoryView patch method
    data = {
        'category_id': category.id,
        'title': 'Updated category',
    }
    response = client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.data['title'] == 'Updated category'


@pytest.mark.django_db
def test_update_category_invalid_user_id(create_user):
    category = Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|i00000:'
    )
    url = reverse('category')  
    data = {
        'category_id': category.id,
        'user_id': 999
    }
    response = client.patch(url, data, format='json')
    assert response.status_code == 400
'''
======================================
# category Delete checklist #
- correct test
- category_id validation
======================================
'''
@pytest.mark.django_db
def test_delete_category_success(create_user):
    category = Category.objects.create(
        user_id=create_user,
        title='Test Category',
        color='#FFFFFF',
        order='0|i00000:'
    )
    url = reverse('category')  
    data = {
        'category_id': category.id
    }
    response = client.delete(url, data, format='json')
    assert response.status_code == 200

    # Check if the category is soft deleted
    category.refresh_from_db()
    assert Category.deleted_at is not None
    assert Category.objects.filter(id=category.id, deleted_at__isnull=True).exists() == False

@pytest.mark.django_db
def test_delete_category_invalid_id(create_user):
    url = reverse('category')  
    data = {
        'category_id': 999
    }
    response = client.delete(url, data, format='json')
    assert response.status_code == 400
