import json
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from ..models import Article
from ..extra_methods import create_slug

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
                slug=create_slug(Article, "Article 1 title")
                )
        self.slug = self.article_1.slug

        self.article_2 = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "tagList":["python"]
                }
        }
        self.article_3 = {
            "article": {
                "title": "Article 3 title",
                "body": "Article body",
                "description": "Article description",
                "tagList":["python", "java"]
                }
        }
        self.article_edit = {
            "article": {
                "title": "Article title - edit",
                "body": "Article body - edit",
                "description": "Article description - edit",
                "tagList":["python", "java"]
                }
            }
        self.article_missing_fields = {
            "article": {
                "title": "Article title - edit",
                "body": "",
                "description": "Article description - edit",
                "tagList":["python", "java"]
                }
            }
        self.url = f"/api/articles/{self.article_1.slug}/"
    def test_create_article_object(self):
        self.assertTrue(self.article_1)
        self.assertTrue(self.article_1.slug)


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
        url_1 = "/api/articles/"
        response_1 = self.client.post(
            url_1,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.get(self.url)

    def test_get_an_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/1232/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_an_article(self):
        self.client.force_authenticate(user=self.user)
        url_1 = "/api/articles/"
        response_1 = self.client.post(
            url_1,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.put(
            self.url,
            content_type="application/json",
            data=json.dumps(self.article_edit)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_an_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/wertr435/"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_an_article_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        url_1 = "/api/articles/"
        response_1 = self.client.post(
            url_1,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.put(
            self.url,
            content_type="application/json",
            data=json.dumps(self.article_missing_fields)
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_an_article(self):
        self.client.force_authenticate(user=self.user)
        url_1 = "/api/articles/"
        response_1 = self.client.post(
            url_1,
            content_type="application/json",
            data=json.dumps(self.article_2)
        )
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_an_article_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/65hg/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
