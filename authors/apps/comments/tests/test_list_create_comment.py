import json
from rest_framework.test import APIClient
from ..models import Comment
from django.contrib.auth import get_user_model
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from django.utils.text import slugify
from authors.apps.articles.models import Article
from authors.apps.articles.extra_methods import create_slug
from authors.apps.comments.tests.base_setup import BaseCommentTests


class TestListCreateComment(BaseCommentTests):
    def test_create_comment_object(self):
        self.assertTrue(self.comment)
        self.assertEqual(self.comment.body, "My first comment")

    def test_cannot_comment_on_comment_without_a_token(self):
        response = self.client.post(
            f"/api/articles/{str(self.article.slug)}/comments/",
            content_type="application/json",
            data=json.dumps({"body": "Fake article"}),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

    def test_cannot_comment_on_comment_without_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        url = f"/api/articles/{self.article.slug}/comments/"
        response = self.client.post(
            url, content_type="application/json", data=json.dumps({"body": ""})
        )
        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["errors"]["body"], ["This field may not be blank."]
        )

    def test_comment_on_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"body": "My first comment"}),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["comment"]["body"], "My first comment")
        self.assertEqual(
            response.data["comment"]["author"]["username"], self.user.username
        )

    def test_get_comments_on_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        self.comment = Comment.objects.create(
            body="My second comment", author=self.profile, article=self.article
        )
        response = self.client.get(
            f"/api/articles/{self.article.slug}/comments/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data["comments"], list))
        self.assertTrue(response.data["commentsCount"], 1)
