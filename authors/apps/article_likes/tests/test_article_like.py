import json
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.articles.extra_methods import create_slug
from ..models import ArticleLike

class TestArticleLikeViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="Zack", email="zack@andela.com", is_superuser=False, is_active=True
        )
        self.article_1 = Article.objects.create(
            slug=create_slug("title of article"),
            title="title of article",
            body="body of article",
            description="description of article",
            author=self.user
        )
        self.article_2 = Article.objects.create(
            slug=create_slug("title of article 2"),
            title="title of article 2",
            body="body of article 2",
            description="description of article 2",
            author=self.user
        )
        self.article_3 = Article.objects.create(
            slug=create_slug("title of article 3"),
            title="title of article 3",
            body="body of article 3",
            description="description of article 3",
            author=self.user
        )
        self.article_like_1 = ArticleLike.objects.create(
            liked_by=self.user,
            article=self.article_2,
            like_value=True
        )
        self.article_dislike = ArticleLike.objects.create(
            liked_by=self.user,
            article=self.article_3,
            like_value=False
        )
    def test_like_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/fake-slug/like"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_like_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.slug}/like"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_article_like_revoke(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_2.slug}/like"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_article_turn_dislike_to_like(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_3.slug}/like"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
    def test_dislike_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/fake-slug/dislike"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_dislike_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.slug}/dislike"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_article_dislike_revoke(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_3.slug}/dislike"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_article_turn_like_to_dislike(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_2.slug}/dislike"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_article_turn_invalid_route(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_2.slug}/dislidfdfsdfke"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

    def test_article_get_like_status(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.slug}/like"
        self.client.post(url)
        url_like_status = f"/api/articles/{self.article_1.slug}/likestatus/"
        response  = self.client.get(url_like_status)
        self.assertEqual(response.status_code, 200)

    def test_article_get_like_none(self):
        self.client.force_authenticate(user=self.user)
        url_like_status = f"/api/articles/{self.article_1.slug}/likestatus/"
        response  = self.client.get(url_like_status)
        self.assertEqual(response.status_code, 200)
