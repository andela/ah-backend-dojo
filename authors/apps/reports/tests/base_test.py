from authors.apps.authentication.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.apps.articles.models import Article
from authors.apps.articles.extra_methods import create_slug

class BaseTest(APITestCase):
    articles_url = '/api/articles/'

    def tearUp(self):
        pass

    def setUp(self):
        self.user = User.objects.create(
            username="lamech", email="lamech@bg.com", is_superuser=False, is_active=True
        )
        self.super_user = User.objects.create(
            username="edward", email="edward@bg.com", is_superuser=True, is_active=True
        )
        self.user_two = User.objects.create(
            username="ann", email="night@bg.com", is_superuser=False, is_active=True
        )
        article_data = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "tagList":["python"]
                }
        }
        self.article_data_2 = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description",
                "tagList":["python"]
                }
        }
        self.report_data = {
            "violation_subject": "rules violation",
            "violation_report": "heieijeei"
        }
        self.report_data_2 = {
            "violation_subject": "spam",
            "violation_report": "this is the first report"
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.articles_url, data=article_data, format='json')
        slug_one = response.data["article"]["slug"]

        

        self.report_articles_url = self.articles_url + "report-article/"
        self.report_article_url_post = self.articles_url + slug_one + "/report-article/"
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

        self.client.force_authenticate(user=self.user_two)
        self.client.post(
            self.report_article_url_post, data=self.report_data_2, format='json'
        )
        response = self.client.get(
            self.report_articles_url, format='json'
        )
        self.report_id = response.data.get('reports')[0].get('id')
        self.report_article_url = self.articles_url + "report-article/" + str(self.report_id) + "/"
        
