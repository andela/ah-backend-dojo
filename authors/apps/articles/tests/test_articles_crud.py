import json

from django.test import TransactionTestCase
from rest_framework.test import APIClient

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.articles.models import ReadingStats


class TestArticleViews(TransactionTestCase):
    fixtures = [
        "authors/fixtures/users.json",
        "authors/fixtures/articles.json",
        "authors/fixtures/tags.json",
    ]

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.get(username="zack")
        self.user_2 = User.objects.get(username="author")
        self.article_1 = Article.objects.get(id=1)

        self.user_admin = User.objects.create(
            username="lamech",
            email="lamech@bg.com",
            is_superuser=True,
            is_active=True,
        )

        self.article_2 = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "tagList": ["python"],
            }
        }
        self.article_3 = {
            "article": {
                "title": "Article 3 title",
                "body": "Article body",
                "description": "Article description",
                "tagList": ["python", "java"],
            }
        }
        self.article_edit = {
            "article": {
                "title": "Article title - edit",
                "body": "Article body - edit",
                "description": "Article description - edit",
                "tagList": ["python"],
            }
        }
        self.article_missing_fields = {
            "article": {
                "title": "Article title - edit",
                "description": "Article description - edit",
                "tagList": ["python", "java"],
            }
        }

        self.report_data = {
            "violation_subject": "rules violation",
            "violation_report": "heieijeei",
        }

    def test_create_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2),
        )
        self.assertEqual(response.status_code, 201)

    def test_slug_creation(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2),
        )
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2),
        )
        self.assertEqual(response.status_code, 201)

    def test_create_an_article_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_missing_fields),
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_articles(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_an_article(self):
        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_view_by_anonymous_user_should_not_increase_the_view_count(
        self
    ):
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["article"]["read_stats"]["views"], 0)
        self.assertEqual(response.data["article"]["read_stats"]["reads"], 0)

        count = ReadingStats.objects.all().filter(article=self.article_1.id)
        self.assertEqual(len(count), 0)

    def test_article_first_time_view_by_authenticated_user_should_increase_the_view_count(
        self
    ):
        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["article"]["read_stats"]["views"], 0)
        self.assertEqual(response.data["article"]["read_stats"]["reads"], 0)

        count = ReadingStats.objects.all().filter(article=self.article_1.id)
        self.assertEqual(len(count), 1)

    def test_article_non_first_time_view_by_authenticated_user_should_not_increase_the_view_count(
        self
    ):
        ReadingStats.objects.create(
            article=self.article_1, user=self.user_2, views=1, reads=0
        )

        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["article"]["read_stats"]["views"], 1)
        self.assertEqual(response.data["article"]["read_stats"]["reads"], 0)

        count = ReadingStats.objects.all().filter(
            article=self.article_1.id, user=self.user_2
        )
        self.assertEqual(len(count), 1)

    def test_first_time_read_by_authenticated_user_should_increase_the_read_count(
        self
    ):

        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/read_stat/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            f"Your read statistics for article with id {self.article_1.id} were registered successfully",
        )

        count = ReadingStats.objects.get(
            article=self.article_1.id, user=self.user_2
        )
        self.assertEqual(count.views, 1)
        self.assertEqual(count.reads, 1)

    def test_not_first_time_read_by_authenticated_user_should_not_increase_the_read_count(
        self
    ):

        ReadingStats.objects.create(
            article=self.article_1, user=self.user_2, views=1, reads=1
        )

        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/read_stat/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            f"Your read statistics for article with id {self.article_1.id} are already registered successfully",
        )

        count = ReadingStats.objects.get(
            article=self.article_1.id, user=self.user_2
        )
        self.assertEqual(count.views, 1)
        self.assertEqual(count.reads, 1)

    def test_article_read_by_author_user_should_not_increase_the_read_count(
        self
    ):

        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}/read_stat/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            "Your Read statistics are not captured for an article you authored",
        )

    def test_get_an_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/1232/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit),
        )
        self.assertEqual(response.status_code, 200)

    def test_update_an_article_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_missing_fields),
        )
        self.assertEqual(response.status_code, 400)

    def test_update_an_article_unauthorized_user(self):
        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit),
        )
        self.assertEqual(response.status_code, 401)

    def test_update_an_article_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/wertr435/"
        response = self.client.put(
            url,
            content_type="application/json",
            data=json.dumps(self.article_edit),
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_an_article(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_an_article_unauthorized_user(self):
        self.client.force_authenticate(user=self.user_2)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_an_article_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/65hg/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_an_article_violated_terms(self):
        # create article by user
        self.client.force_authenticate(user=self.user)
        url = "/api/articles/"
        response = self.client.post(
            url,
            content_type="application/json",
            data=json.dumps(self.article_2),
        )
        article_id = response.data["article"]["id"]
        slug_one = response.data["article"]["slug"]

        # report article by user_2
        report_article_url_post = f"{url}{slug_one}/report-article/"
        self.client.force_authenticate(user=self.user_2)
        self.client.post(
            report_article_url_post, data=self.report_data, format="json"
        )
        report_articles_url = url + "report-article/"

        # update report status and delete
        response_report = self.client.get(report_articles_url, format="json")
        report_id = response_report.data.get("reports")[0].get("id")
        report_data_2 = {"report_status": "allegations_true"}
        self.client.force_authenticate(user=self.user_admin)
        report_article_url = f"{url}report-article/{str(report_id)}/"
        self.client.put(report_article_url, data=report_data_2, format="json")
        response = self.client.delete(f"{url}{article_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            "Reported article has been deleted successfully",
        )

    def test_delete_an_article_hasnt_violated_terms(self):
        self.client.force_authenticate(user=self.user_admin)
        url = f"/api/articles/{self.article_1.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["error"],
            "No proof yet that this article has violated any terms of service",
        )
