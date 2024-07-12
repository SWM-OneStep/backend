from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from todos.models import Todo
from accounts.models import User
from django.utils import timezone
import json


class TodoCreateTestCase(APITestCase):
    def setUp(self):
        # Create a user for the tests
        self.user = User.objects.create(email='testuser@asdf.asdf')
        
        # Log in the user
        self.client.force_authenticate(user=self.user)

    # start_date 가 deadline 보다 빠른 경우 
    def test_start_date_is_earlier_than_deadline(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-03',
                'deadline': '2021-01-01',
                'content': '',
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'deadline must be on or after start_date.'})

    # content 가 빈 문자열이거나 0자 이하인 경우
    def test_content_is_null(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-03',
                'content': '',
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'content must be between 1 and 50 characters.'})

    # content 가 51자 이상인 경우
    def test_content_is_over_50(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'a'*51,
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'content must be between 1 and 50 characters.'})

    # 카테고리가 #헥스 값이 아닌경우
    def test_category_is_not_hex(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'test',
                'category': 'FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'category must be a valid hex color code.'})

    # parent_id 가 자기 자신인 경우
    def test_parent_id_is_self(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'test',
                'category': '#FFFFFF',
                'parent_id': 1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'parent_id cannot be the same as todo_id.'})

    # user_id 가 없는 id 인 경우
    def test_user_id_is_not_exist(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': 999,
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'test',
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'user_id does not exist.'})

    # parent_id 가 없는 id 인 경우 -> 너는 성공해야해... 
    def test_parent_id_is_not_exist(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'test',
                'category': '#FFFFFF',
                'parent_id': 999
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'parent_id does not exist.'})

    # user_id 가 없는경우
    def test_user_id_is_null(self):
        response = self.client.post(
            reverse('todos'),
            {
                'start_date': '2021-01-01',
                'deadline': '2021-01-01',
                'content': 'test',
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, {'error': 'user_id is required.'})

    # 올바르게 입력된 경우 
    def test_correct_input(self):
        response = self.client.post(
            reverse('todos'),
            {
                'user_id': self.user.id,
                'start_date': '2021-01-01',
                'deadline': '2021-01-03',
                'content': 'test',
                'category': '#FFFFFF',
                'parent_id': ''
            }
        )
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TodoGetTestCase(APITestCase):
    def setUp(self):
        self. client = APIClient()

    # user_id 가 없는 경우

    # user_id 가 없는 id 인 경우 

    # start_date 나 end_date 중 하나만 주어진 경우 

    # start_date, user_id, end_date 가 모두 주어진 경우

    # user_id 만 주어진 경우

    # 삭제된 todo를 가져오는 경우 

    # 올바르게 입력된 경우 


class TodoUpdateTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    # user_id 가 없는 경우

    # user_id 가 없는 id 인 경우

    # todo_id 가 없는 경우

    # todo_id 가 없는 id 인 경우

    # 한개의 업데이트 내용이 포함된 경우

    # 여러개의 업데이트 내용이 포함된 경우

class TodoDeleteTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    # user_id 가 없는 경우

    # user_id 가 없는 id 인 경우

    # todo_id 가 없는 경우

    # todo_id 가 없는 id 인 경우

    # 올바르게 입력된 경우
