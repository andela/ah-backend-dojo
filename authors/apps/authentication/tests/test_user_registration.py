from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
import json
import pytest
from ..models import User


class TestQuestionViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = {
            "user": {
                "username": "Jajcob",
                "email": "jakk@ejake.jake",
                "password": "444444444",
            }
        }
        self.user2 = User.objects.create(
            username="Jajcob", email="jakk@ejake.jake", is_superuser=False
        )

    def test_register_password_without_capital_letter(self):

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["password"][0],
            "Password should contain at least one Upper Case letter",
        )

    def test_register_password_without_atleast_one_lower_letter(self):

        self.user["user"]["password"] = "444444R444"
        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["password"][0],
            "Password should contain at least one lower Case letter",
        )

    def test_register_password_without_non_alphanumeric_password(self):

        self.user["user"]["password"] = "Password"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["password"][0],
            "Password should be alpha Numeric",
        )

    def test_register_password_with_length_less_than_8_characters(self):

        self.user["user"]["password"] = "Passw89"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["password"][0],
            "Ensure this field has at least 8 characters.",
        )

    def test_register_with_duplicate_user(self):
        self.client.force_authenticate(self.user2)

        self.user["user"]["password"] = "Passw89"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["username"][0],
            "user with this username already exists.",
        )
        self.assertEqual(
            response.data["errors"]["email"][0],
            "user with this email already exists.",
        )

    def test_register_without_password(self):

        self.user["user"]["password"] = ""

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["password"][0],
            "This field may not be blank.",
        )

    @pytest.mark.xfail
    def test_register_with_password_same_as_username(self):

        self.user["user"]["username"] = "Kalmuiygsic123"
        self.user["user"]["email"] = "Kalmsic123@mail.com"

        self.user["user"]["password"] = "Kalmuiygsic123"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["username"][0],
            "Password cannot be the same as the username",
        )

    def test_register_with_space_character_in_username(self):

        self.user["user"]["username"] = "Kalmsi  c123"
        self.user["user"]["email"] = "Kalmsic123@mail.com"

        self.user["user"]["password"] = "Kalmuiygsic123"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["username"][0],
            "Username cannot contain a space",
        )

    def test_register_a_user_successfully(self):

        self.user["user"]["password"] = "Password123.l"
        self.user["user"]["email"] = "arthur@email.com"
        self.user["user"]["username"] = "kalsmic"

        response = self.client.post(
            "/api/users/",
            content_type="application/json",
            data=json.dumps(self.user),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {"email": "arthur@email.com", "username": "kalsmic"}
        )
