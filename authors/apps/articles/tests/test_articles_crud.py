import json
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from ..models import Article

class TestArticleViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="zack", email="zack@andela.com", is_superuser=False, is_active=True
        )
        self.article_1 = Article.objects.create(
                title="Article 1 title",
                body="Article body",
                description="Article description",
                author=self.user,
                )
        self.article_2 = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description"
                }
        }
        self.article_3 = {
            "article": {
                "title": "Article 3 title",
                "body": "Article body",
                "description": "Article description"
                }
        }
        self.article_edit = {
            "article": {
                "title": "Article title - edit",
                "body": "Article body - edit",
                "description": "Article description - edit"
                }
            }
        self.article_missing_fields = {
            "article": {
                "title": "Article title - edit",
                "body": "",
                "description": "Article description - edit"
                }
            }

    def test_create_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        self.assertEqual(response.status_code, 201)

    def test_slug_creation(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        self.assertEqual(response.status_code, 201)

    def test_create_an_article_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_missing_fields)
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_articles(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_an_article_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/1232"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_an_article_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/123"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_an_article_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_missing_fields)
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_an_article_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/1234"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
