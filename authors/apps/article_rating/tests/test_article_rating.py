from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.article_rating.tests.base_test import BaseTest

class TestArticleRating(BaseTest):

    def test_post_rating_success(self):
        response = self.client.post(
            self.rate_article_url_one + "5/", format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rating_self_authored(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.rate_article_url_one + "5/", format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_rating_success(self):
        self.client.post(
            self.rate_article_url_one + "3/",format='json'
        )
        response = self.client.post(
            self.rate_article_url_one + "5/", format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rating_out_of_range(self):
        response = self.client.post(
            self.rate_article_url_one + "7/",  format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_rating_string(self):
        response = self.client.post(
            self.rate_article_url_one + "this/", format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
