from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.article_rating.tests.base_test import BaseTest

class TestAverageArticleRating(BaseTest):

    def test_view_article_rating(self):
        response = self.client.get(
            self.rate_article_url_one + "average/", format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)