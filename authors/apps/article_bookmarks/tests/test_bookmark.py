from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from authors.apps.article_bookmarks.models import Bookmark
from authors.apps.articles.extra_methods import create_slug
from authors.apps.articles.models import Article


class TestBookmark(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            username="kalsmic",
            password="Pa$$word234",
            email="kalsmic@kalsmic.kalsmic",
            is_active=True,
            is_email_verified=True,
        )

        self.user2 = get_user_model().objects.create(
            username="arthur",
            password="Pa$$word234",
            email="email@email.arthur",
            is_active=True,
            is_email_verified=True,
        )

        self.article = Article.objects.create(
            title="Article 1 title",
            body="Article body",
            description="Article description",
            author=self.user,
            slug=create_slug("Article 1 title"),
        )
        self.article2 = Article.objects.create(
            title="Article 2 title",
            body="Article body",
            description="Article description",
            author=self.user,
            slug=create_slug("Article 2 title"),
        )
        self.slug = self.article2.slug

        self.bookmark = Bookmark.objects.create(
            user=self.user, article=self.article
        )
        self.auth_error = {
            "detail": "Authentication credentials were not provided."
        }
        self.not_found = {"detail": "Not Found"}

    def test_models(self):
        self.assertTrue(self.user)
        self.assertTrue(self.user2)
        self.assertTrue(self.article)
        self.assertTrue(self.bookmark)

    def test_anonymous_user_cannot_bookmark_an_article(self):
        response = self.client.post(f"/api/articles/{self.slug}/bookmark/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.auth_error)

    def test_authenticated_user_cannot_add_a_bookmark_with_invalid_article_slug(
        self
    ):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(f"/api/articles/doesnotexist/bookmark/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "Not found.")

    def test_authenticated_user_can_bookmark_an_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")

        response = self.client.post(f"/api/articles/{self.slug}/bookmark/")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["message"], "Article Bookmarked Successfully"
        )
        self.assertEqual(
            response.data["bookmark"]["article"], self.article2.id
        )
        self.assertIn(
            "id",
            response.data["bookmark"],
            "bookmark id must be present in response",
        )

    def test_anonymous_user_should_not_get_bookmarks_list(self):
        response = self.client.get("/api/bookmarks/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.auth_error)

    def test_authenticated_user_should_get__bookmarks_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.get("/api/bookmarks/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertIsInstance(response.data["bookmarks"], list)
        self.assertEqual(response.data["bookmarks"][0]["id"], self.bookmark.id)

    def test_user_can_a_duplicate_bookmark(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        slug = self.bookmark.article.slug

        response = self.client.post(f"/api/articles/{slug}/bookmark/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            "Article has been unBookmarked Successfully",
        )

    def test_unauthenticated_user_cannot_check_bookmark_status(self):
        response = self.client.get("/api/articles/{slug}/bookmark_status/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.auth_error)

    def test_authenticated_user_can_check_bookmark_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        self.client.post(f"/api/articles/{self.slug}/bookmark/")

        response = self.client.get(f"/api/articles/{self.slug}/bookmark_status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['isBookmarked'], True)

    def test_isBookmarked_is_false_when_the_article_is_not_bookmarked(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user2.token}")
        response = self.client.get(f"/api/articles/{self.slug}/bookmark_status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['isBookmarked'], False)
