from authors.apps.authentication.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.apps.articles.models import Article
from authors.apps.articles.extra_methods import create_slug

class TestShareArticle(APITestCase):
    articles_endpoint = '/api/articles/'
    

    def setUp(self):
        self.user = User.objects.create(
            username="lamech", email="lamech@bg.com", is_superuser=False, is_active=True
        )
        article_data = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "tagList":["python"]
                }
        }
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.articles_endpoint, data=article_data, format='json')
        self.article_id_1 = response.data.get("article").get("id")
        self.facebook_share_url = f"{self.articles_endpoint}{self.article_id_1}/facebookshare/"
        self.twitter_share_url = f"{self.articles_endpoint}{self.article_id_1}/twittershare/"
        self.email_share_url = f"{self.articles_endpoint}{self.article_id_1}/emailshare/"

    def test_share_on_facebook(self):
         response = self.client.post(self.facebook_share_url, format='json')
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertTrue("share_link" in response.data)

    def test_share_on_twitter(self):
         response = self.client.post(self.twitter_share_url, format='json')
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertTrue("share_link" in response.data)

    def test_share_in_email(self):
        response = self.client.post(self.email_share_url, data={"email":"testingandela@gmail.com"},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("message" in response.data)
