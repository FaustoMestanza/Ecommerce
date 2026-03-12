from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create a user to test listing
        User.objects.create_user(username="testuser", password="pass")

    def test_list_users(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_create_user(self):
        url = reverse("user-list")
        payload = {"username": "newuser", "password": "newpass"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())
