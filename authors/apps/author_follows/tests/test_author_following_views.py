import json
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from ..models import AuthorFollowing

class TestAuthorFollowViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_user = User.objects.create(
            username="James", email="j.mudidi@andela.com", is_superuser=False, is_active=True
        )
        self.user_1 = User.objects.create(
            username="Zack", email="zack@andela.com", is_superuser=False, is_active=True
        )
        self.user_2 = User.objects.create(
            username="Adralia", email="nelson.a@andela.com", is_superuser=False, is_active=True
        )
        self.followed = AuthorFollowing.objects.create(
            follower="Zack",
            following=self.login_user 
        )
    
    def test_get_followed(self):
        self.client.force_authenticate(user=self.login_user)
        url_1 = f"/api/authors/{self.user_1.username}/follow/"
        self.client.post(url_1)
        url_2 = "/api/authors/following/"
        response = self.client.get(url_2)
        self.assertEqual(response.status_code, 200)
    
    def test_get_followers(self):
        self.client.force_authenticate(user=self.login_user)
        url = "/api/authors/followers/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_following_author(self):
        self.client.force_authenticate(user=self.login_user)
        url = f"/api/authors/{self.user_1.username}/follow/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "you have followed Zack"})
    
    def test_unfollowing_author(self):
        self.client.force_authenticate(user=self.login_user)
        url = f"/api/authors/{self.user_1.username}/follow/"
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
    
    def test_following_yourself_error(self):
        self.client.force_authenticate(user=self.login_user)
        url = f"/api/authors/{self.login_user.username}/follow/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
    
    def test_get_followers_followed_invalid_url(self):
        self.client.force_authenticate(user=self.login_user)
        url = "/api/authors/sadfasdf/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    