from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_payload = {
            "id": 11,
            "username": "alice",
            "email": "alice@test.com",
            "is_staff": False,
            "is_active": True,
        }

    def _token_for_user(self, user_id: int) -> str:
        refresh = RefreshToken()
        refresh["user_id"] = user_id
        return str(refresh.access_token)

    def test_anonymous_cannot_access_me(self):
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("apps.authentication.views.authenticate_user")
    def test_login_returns_access_and_refresh_tokens(self, mock_authenticate_user):
        mock_authenticate_user.return_value = (status.HTTP_200_OK, self.user_payload)

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "alice", "password": "alicepass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    @patch("apps.authentication.views.get_user_by_id")
    def test_authenticated_user_can_access_me(self, mock_get_user_by_id):
        mock_get_user_by_id.return_value = (status.HTTP_200_OK, self.user_payload)
        token = self._token_for_user(self.user_payload["id"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_payload["username"])

    @patch("apps.authentication.views.register_user")
    def test_register_is_rate_limited(self, mock_register_user):
        mock_register_user.return_value = (
            status.HTTP_201_CREATED,
            {"id": 999, "username": "created"},
        )

        cache.clear()
        url = reverse("auth-register")
        responses = []

        for i in range(6):
            responses.append(
                self.client.post(
                    url,
                    {
                        "username": f"user_{i}",
                        "email": f"user_{i}@test.com",
                        "password": "longpass123",
                    },
                    format="json",
                )
            )

        for response in responses[:5]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(responses[5].status_code, status.HTTP_429_TOO_MANY_REQUESTS)
