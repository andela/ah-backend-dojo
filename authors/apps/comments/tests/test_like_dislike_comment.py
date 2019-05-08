import json
from rest_framework.test import APIClient, APITestCase
from authors.apps.authentication.models import User
from authors.apps.comments.tests.base_setup import BaseCommentTests

class TestDislikeAndLikeCommment(BaseCommentTests):
    """Test Dislike And Like Comment."""

    def test_user_can_like_a_comment(self):
        """Test like a comment, get likes on a 
                  comment and dislike a comment """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        self.assertEqual(response.status_code, 201)
        response1 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/1/like",
            content_type="application/json",
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(
            response1.data["message"],
            "You have liked this comment",
        )
        response2 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/1/like",
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data["message"],
            "You have already liked this comment",
        )

        response3 = self.client.get(
            f"/api/articles/{self.article.slug}/comments/1/like",
            content_type="application/json",
        )
        self.assertEqual(response3.status_code, 200)

        response4 = self.client.delete(
            f"/api/articles/{self.article.slug}/comments/1/dislike",
            content_type="application/json",
        )
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(
            response4.data["message"],
            "Your like has been successfully revoked",
        )
        response5 = self.client.delete(
            f"/api/articles/{self.article.slug}/comments/1/dislike",
            content_type="application/json",
        )
        self.assertEqual(response5.status_code, 400)
        self.assertEqual(
            response5.data["message"],
            "You have not liked this comment",
        )
        