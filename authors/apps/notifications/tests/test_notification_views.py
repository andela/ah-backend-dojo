import json
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.articles.extra_methods import create_slug
from authors.apps.authentication.models import User
from authors.apps.author_follows.models import AuthorFollowing
from authors.apps.articles.models import Article, FavoriteArticle
from authors.apps.comments.models import Comment

class TestAuthorFollowViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create(
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
            following=self.author 
        )
        self.article = Article.objects.create(
            slug=create_slug("title of article"),
            title="title of article",
            body="body of article",
            description="description of article",
            author=self.author
        )
    
    def test_get_my_notifications(self):
        self.client.force_authenticate(user=self.user_1)
        url = f"/api/notifications/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["notifications_count"], 1)
    
    def test_deactivate_notifications(self):
        self.client.force_authenticate(user=self.user_1)
        url = f"/api/notify/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "you have deactivated notifications")
    
    def test_activate_notifications(self):
        self.client.force_authenticate(user=self.user_1)
        url = f"/api/notify/"
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "you have activated notifications")
