from django.urls import reverse
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from django_rest_passwordreset.models import ResetPasswordToken
import json
import pytest
from ..models import User


class TestUserRegistrationView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(
            username="bison",
            email="bisonlou@gmail.com",
            password="Pa$$word123",
            is_superuser=False,
            is_active=True,
        )

    def test_email_is_sent(self):
        data = {"email": "bisonlou@gmail.com"}
        url = reverse("password_reset:reset-password-request")
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(data),
            HTTP_USER_AGENT="Mozilla/5.0",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "OK")

    def test_successful_password_reset(self):
        token = ResetPasswordToken.objects.create(user=self.user)

        kwargs = {"token": token.key}

        url = reverse("password_reset_verify_token", kwargs=kwargs)
        data = {"password": "Pa$$word1234"}

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"], "Password reset succesfully"
        )

    def test_invalid_token(self):
        token = ResetPasswordToken.objects.create(user=self.user)
        kwargs = {"token": str(token.key) + "ji"}

        url = reverse("password_reset_verify_token", kwargs=kwargs)

        data = {"password": "Pa$$word1234"}

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "invalid token")

    def test_expired_token(self):
        settings.DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = -1
        token = ResetPasswordToken.objects.create(user=self.user)
        kwargs = {"token": str(token.key)}

        url = reverse("password_reset_verify_token", kwargs=kwargs)
        data = {"password": "Pa$$word1234"}

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Token expired")

        settings.DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 24