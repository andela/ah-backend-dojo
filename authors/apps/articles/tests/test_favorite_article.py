import json
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.articles.extra_methods import create_slug
from rest_framework import status



class FavoriteArticle(TestCase):
    """
    Tests for Favoring Articles
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="zack", email="zack@andela.com", is_superuser=False, is_active=True
        )
        self.user_2 = User.objects.create(
            username="author", email="author@andela.com", is_superuser=False, is_active=True
        )
        self.article_1 = Article.objects.create(
                slug=create_slug(Article, "Article 1 title"),
                title="Article 1 title",
                body="Article body",
                description="Article description",
                author=self.user
                )

    def test_favorite_an_article(self):
        """
        Test favorite an article
        """
        self.client.force_authenticate(user=self.user)
        url_1 = f"/api/articles/{self.article_1.slug}/favorite/"
        response = self.client.post(url_1)
        self.assertEqual(response.status_code, 200)

    def test_article_has_already_been_favorited_by_a_user(self):
        """
        Test user cann't favorite an article twice
        """
        self.client.force_authenticate(user=self.user)
        url_1 = f"/api/articles/{self.article_1.slug}/favorite/"
        self.client.post(url_1)
        response = self.client.post(url_1)
        self.assertEqual(response.status_code, 200)

    def test_unfavorite_an_article(self):
        """
        Test Unfavorite an article
        """
        self.client.force_authenticate(user=self.user)
        url_1 = f"/api/articles/{self.article_1.slug}/favorite/"
        self.client.post(url_1)
        url_2 = f"/api/articles/{self.article_1.slug}/unfavorite/"
        response = self.client.delete(url_2)
        self.assertEqual(response.status_code, 200)

    def test_unfavorite_an_article_without_favoriting(self):
        """
        Test unfavorite an article without having favorited it.
        """
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.slug}/unfavorite/"
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
