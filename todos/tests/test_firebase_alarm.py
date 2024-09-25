import unittest
from unittest.mock import patch
from django.test import TestCase
from todos.firebase_messaging import send_push_notification, PUSH_NOTIFICATION_SUCCESS

class FCMNotificationTest(TestCase):

    @patch("todos.firebase_messaging.send_push_notification")
    def test_send_push_notification(self, mock_send_fcm):
        mock_send_fcm.return_value = PUSH_NOTIFICATION_SUCCESS
        mock_send_fcm()
        response = send_push_notification("device_token", "title", "message")
        mock_send_fcm.assert_called_once()
        self.assertEqual(response, PUSH_NOTIFICATION_SUCCESS)


if __name__ == '__main__':
    unittest.main()
