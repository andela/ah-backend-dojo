from authors.apps.authentication.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

class BaseTest(APITestCase):
    create_article_url = '/api/articles/'

    def setUp(self):
        self.user = User.objects.create(
            username="lamech", email="lamech@bg.com", is_superuser=False
        )
        user_two = User.objects.create(
            username="ann", email="night@bg.com", is_superuser=False
        )
        article_data = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "article_tags":["python"]
                }
        }
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.create_article_url, data=article_data, format='json')
        slug_one = response.data.get("article").get("slug")
        self.rate_article_url_one = self.create_article_url + slug_one + "/article-rating/"
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=user_two)