import json

from django.test import TestCase
from rest_framework.test import APIClient

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.articles.extra_methods import create_slug
from authors.apps.article_tag.models import ArticleTag


class TestArticleSearch(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(
            username="bison",
            email="bisonlou@gmail.com",
            is_superuser=False,
            is_active=True
        )

        self.mechanics_tag = ArticleTag.objects.create(
            tag_text='Mechanics'
        )

        self.statistics_tag = ArticleTag.objects.create(
            tag_text='Statistics'
        )

        self.pure_tag = ArticleTag.objects.create(
            tag_text='Pure'
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.mechanics_article = Article.objects.create(
            slug="slug-1",
            title="Mechanics",
            body="Mathematics II",
            description="By AJ Saddler",
            author=self.user,
        )

        self.pure_article = Article.objects.create(
            slug="slug-2",
            title="Pure Math",
            body="Mathematics I",
            description="By Backhouse",
            author=self.user,
        )

        self.statistics_article = Article.objects.create(
            slug="slug-3",
            title="Statistics",
            body="Mathematics III",
            description="By Mukose",
            author=self.user,
        )

        self.pure_article.tagList.add(
            self.pure_tag
        )

        self.mechanics_article.tagList.add(
            self.mechanics_tag
        )

        self.statistics_article.tagList.add(
            self.statistics_tag
        )

    def test_filter_articles_by_author(self):
        url = f"/api/articles/?author=bison"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"]["articles"][0]["author"], "bison"
        )
        self.assertEqual(response.data["count"], 3)

    def test_filter_articles_by_tag(self):
        url = f"/api/articles/?tag=Pure"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_filter_articles_by_title(self):
        url = f"/api/articles/?title=Mechanics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_filter_articles_by_search(self):
        url = f"/api/articles/?search=Mathematics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)

    def test_filter_articles_by_description(self):
        url = f"/api/articles/?search=By Mukose"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
