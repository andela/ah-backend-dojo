from django.urls import reverse
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import json
import pytest
from ..models import User


class TestUserRegistrationView(TestCase):
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
        self.assertEqual(response.data["email"], "arthur@email.com")
        self.assertEqual(response.data["username"], "kalsmic")
        self.assertIn("token",response.data)

    def test_succesful_user_activation(self):
        '''
        Ensure that a user is succesfully activated
        '''
        uid = self.user2.id
        kwargs = {
        "uidb64": urlsafe_base64_encode(force_bytes(uid)).decode(),
        "token": default_token_generator.make_token(self.user2)
    }
        activation_url = reverse("activate_user_account", kwargs=kwargs)
        self.assertFalse(self.user2.is_active)

        response = self.client.get(
           activation_url,
           content_type="application/json",
        )
        self.assertEqual(response.data, "Activation successful")

    def test_user_activation_with_non_existent_user(self):
        '''
        Ensures that a user who does not exist cannot be activated
        '''
        uid = 10
        kwargs = {
        "uidb64": urlsafe_base64_encode(force_bytes(uid)).decode(),
        "token": default_token_generator.make_token(self.user2)
        }

        activation_url = reverse("activate_user_account", kwargs=kwargs)
        self.assertFalse(self.user2.is_active)

        response = self.client.get(
           activation_url,
           content_type="application/json",
        )
        self.assertEqual(response.data, "Activation failed")

    def test_user_activation_expiry(self):
        '''
        Ensures that an activation can expire
        '''
        uid = self.user2.id

        kwargs = {
        "uidb64": urlsafe_base64_encode(force_bytes(uid)).decode(),
        "token": default_token_generator.make_token(self.user2)
        }

        activation_url = reverse("activate_user_account", kwargs=kwargs)
        self.assertFalse(self.user2.is_active)
        settings.PASSWORD_RESET_TIMEOUT_DAYS = -1

        response = self.client.get(
           activation_url,
           content_type="application/json",
        )
        self.assertEqual(response.data, "Activation link has expired")

