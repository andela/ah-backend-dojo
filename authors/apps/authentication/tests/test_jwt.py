from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
import json

from ..models import User
from rest_framework.exceptions import AuthenticationFailed

import jwt

from datetime import datetime, timedelta

from django.conf import settings


def custom_token(user_id, exp):
    token = jwt.encode(
        {
            "id": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=exp),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    ).decode("utf-8")
    return token


class JWTEndpointProtectionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = {
            "username": "Michael",
            "email": "email@email.com",
            "password": "Password123.k",
        }
        self.user3 = User.objects.create(
            username="arthur",
            email="arthur@dummyah-.com",
            is_superuser=False,
            password="Passeord123m,.",
        )
        self.token = self.user3.token

    def test_few_authorization_header_arguments(self):
        """Authorization header missing either prefix or token"""

        self.client.credentials(HTTP_AUTHORIZATION="bjhvcfubbknbkbnkkl")
        response = self.client.get("/api/welcome/")
        self.assertEqual(response.data["detail"], "Invalid Access Token")
        self.assertEqual(response.status_code, 403)

    def test_token_with_missing_bearer_prefix(self):
        """JWT token must contain both a Bearer prefix and the token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"bearer {self.token}")
        response = self.client.get("/api/welcome/")
        self.assertEqual(
            response.data["detail"], "Bearer Missing in Authorizarion header"
        )
        self.assertRaises(AuthenticationFailed)
        self.assertEqual(response.status_code, 403)

    def test_token_with_invalid_user_id(self):
        """JWT token must contain a a valid user id"""
        token_with_invalid_id = custom_token(1, 3)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_with_invalid_id}"
        )
        response = self.client.get("/api/welcome/")
        self.assertEqual(
            response.data["detail"],
            "Invalid user Token, please register an account to acquire valid login credentials.",
        )
        self.assertEqual(response.status_code, 403)

    def test_expired_token_raises_expired_signature_error(self):
        """User should not access protected endpoints with an expired JWT Token"""
        user_id = self.user3.id
        expired_token = custom_token(int(user_id), -3)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        response = self.client.get("/api/welcome/")
        self.assertRaises(jwt.ExpiredSignatureError)
        self.assertEqual(response.data["detail"], "Access Token expired")
        self.assertEqual(response.status_code, 403)

    def test_invalid_jwt_token_raises_an_invalid_token_exception(self):
        """Invalid jwt token raises in invalid token error when decoding it"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fdfdfdfdf")
        response = self.client.get("/api/welcome/")
        self.assertRaises(jwt.InvalidTokenError)
        self.assertEqual(
            response.data["detail"], "Error decoding access Token"
        )
        self.assertEqual(response.status_code, 403)

    def test_user_can_access_a_protected_endpoint_with_a_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/welcome/")
        self.assertEqual(response.data["message"], "Hello, world!")
        self.assertEqual(response.status_code, 200)
