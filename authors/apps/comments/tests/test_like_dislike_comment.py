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

        comment_id = response.data.get("comment").get("id")

        self.assertEqual(response.status_code, 201)
        response1 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(
            response1.data["message"],
            "You have successfully liked this comment",
        )
        response2 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data["message"],
            "You have successfully revoked your like on this comment",
        )

        response3 = self.client.get(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )
        self.assertEqual(response3.status_code, 200)

    def test_comment_change_dislike_to_like(self):
        """test if a user can like a comment they previusly disliked"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)
        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )
  
        response2 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data.get("message"),
            "You now like this comment",
        )
        
    def test_user_revoke_dislike(self):
        """test if a user can undo a dislike of a comment they 
            previusly disliked"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)
        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )

        response2 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data.get("message"),
            "You have successfully revoked your dislike on this comment",
        )

    def test_user_change_like_to_dislike(self):
        """test if a user can dislike a comment they previusly liked"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)
        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )

        response2 = self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data.get("message"),
            "You now dislike this comment",
        )

    def test_user_get_dislikes_count(self):
        """test if a user can get number of dislikes"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)
        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )

        self.client.get(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
        )

        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )

        response2 = self.client.get(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)

    def test_user_get_like_status(self):
        """test if a user can get the state of a like/dislike of a 
        comment"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)
        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/like",
            content_type="application/json",
        )

        self.client.post(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/dislike",
            content_type="application/json",
        )

        response2 = self.client.get(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/likestatus",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data.get("status"),
            False,
        )

    def test_user_get_like_none(self):
        """test if a user can get the state of like or dislike 
        if they have never liked or disliked a comment"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user.token}")
        response = self.client.post(
            f"/api/articles/{self.article.slug}/comments/",
            content_type="application/json",
            data=json.dumps({"comment":{"body": "Fake article"}}),
        )
        comment_id = response.data.get("comment").get("id")
        self.assertEqual(response.status_code, 201)

        response2 = self.client.get(
            f"/api/articles/{self.article.slug}/comments/{comment_id}/likestatus",
            content_type="application/json",
        )
    
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data.get("status"),
            "none",
        )
        