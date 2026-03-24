from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
        )
        self.alice = User.objects.create_user(
            username="alice",
            email="alice@test.com",
            password="alicepass123",
        )
        self.bob = User.objects.create_user(
            username="bob",
            email="bob@test.com",
            password="bobpass123",
        )

    def auth(self, user):
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_anonymous_cannot_list_users(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_admin_can_list_users(self):
        self.auth(self.admin)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 3)

    def test_regular_user_cannot_list_users(self):
        self.auth(self.alice)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_retrieve_own_record(self):
        self.auth(self.alice)
        url = reverse("user-detail", kwargs={"pk": self.alice.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "alice")

    def test_user_cannot_retrieve_other_user_record(self):
        self.auth(self.alice)
        url = reverse("user-detail", kwargs={"pk": self.bob.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_user_requires_password(self):
        url = reverse("user-list")
        payload = {"username": "newuser"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_anonymous_can_register_user_with_password(self):
        url = reverse("user-list")
        payload = {"username": "newuser", "password": "newpass123"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_is_rate_limited(self):
        cache.clear()
        url = reverse("user-list")

        responses = []
        for i in range(6):
            responses.append(
                self.client.post(
                    url,
                    {"username": f"throttle_{i}", "password": "pass12345"},
                    format="json",
                )
            )

        for response in responses[:5]:
            self.assertEqual(response.status_code, 201)
        self.assertEqual(responses[5].status_code, 429)
