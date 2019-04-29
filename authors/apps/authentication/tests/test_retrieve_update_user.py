from django.test import TestCase
from rest_framework.test import APIClient
import json
from ..models import User


class TestRetrieveUpdateViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = {
            "user": {
                "username": "kalsmic",
                "email": "kalsmic@gmail.com",
                "password": "444444444",
            }
        }
        self.user2 = User.objects.create(
            username="kalsmic", email="kalsmic@email.com", is_superuser=False
        )
        self.user3 = User.objects.create(
            username="user3", email="user3@email.com", is_superuser=False
        )

    def test_retrieve_user_with_invalid_token(self):
        response = self.client.get("/api/user/")
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )
        self.assertEqual(response.status_code, 403)

    def test_retrieve_user_with_valid_token(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get("/api/user/")
        self.assertEqual(response.data["username"], "kalsmic")
        self.assertEqual(response.data["email"], "kalsmic@email.com")

        self.assertEqual(response.status_code, 200)

    def test_update_user_with_user_without_token(self):
        response = self.client.put("/api/user/")
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_user_with_user_with_invalid_email(self):
        response = self.client.put("/api/user/")
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_user_without_providing_a_username_or_email(self):
        self.user3.is_active = True
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user3.token}"
        )
        response = self.client.put(
            "/api/user/",
            content_type="application/json",
            data=json.dumps({"user": {"email": "", "username": ""}}),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["username"][0],
            "This field may not be blank.",
        )
        self.assertEqual(
            response.data["errors"]["email"][0], "This field may not be blank."
        )

    def test_update_user_invalid_email_format(self):
        self.user3.is_active = True
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user3.token}"
        )
        response = self.client.put(
            "/api/user/",
            content_type="application/json",
            data=json.dumps({"user": {"email": "mail.com"}}),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["email"][0], "Enter a valid email address."
        )

    def test_update_user_with_username_or_email_which_already_exists(self):
        self.user2.is_active = True
        self.user3.is_active = True
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user3.token}"
        )
        response = self.client.put(
            "/api/user/",
            content_type="application/json",
            data=json.dumps(
                {
                    "user": {
                        "email": self.user2.email,
                        "username": self.user2.username,
                    }
                }
            ),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["email"],
            ["user with this email already exists."],
        )
        self.assertEqual(
            response.data["errors"]["username"],
            ["user with this username already exists."],
        )

    def test_update_user_with_user_with_valid_data(self):
        self.user2.is_active = True
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user2.token}"
        )
        response = self.client.put(
            "/api/user/",
            content_type="application/json",
            data=json.dumps({"user": {"email": "arthurkalule@gmail.com"}}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {"email": "arthurkalule@gmail.com", "username": "kalsmic"},
        )
