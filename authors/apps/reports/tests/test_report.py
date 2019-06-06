
from rest_framework import status
from authors.apps.reports.tests.base_test import BaseTest

class TestArticleReport(BaseTest):

    def test_post_report_success(self):
        response = self.client.post(
            self.report_article_url_post, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_report_missing_subject(self):
        self.report_data = {
            "violation_report": "heieijeei"
        }
        response = self.client.post(
            self.report_article_url_post, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_report_missing_details(self):
        self.report_data = {
            "violation_subject": "theieienjb",
        }
        response = self.client.post(
            self.report_article_url_post, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_report_missing_article(self):
        self.report_article_url_post = self.articles_url + "this-is-slug" + "/report-article/"
        response = self.client.post(
            self.report_article_url_post, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_report_own_article(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.report_article_url_post, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_report_not_found(self):
        self.report_article_url = self.articles_url + "report-article/10000/"
        self.client.force_authenticate(user=self.super_user)
        response = self.client.put(
            self.report_article_url, data=self.report_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_report_not_found(self):
        self.report_article_url = self.articles_url + "report-article/10000/"
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(
            self.report_article_url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_report_admin(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_report_author(self):
        response = self.client.get(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_report_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_report_authorized(self):
        response = self.client.delete(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_report_none(self):
        self.report_id = 1000
        self.report_article_url = self.articles_url + "report-article/" + str(self.report_id) + "/"
        response = self.client.delete(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_report_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_report_list(self):
        response = self.client.get(
            self.report_articles_url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_report_admin_denied(self):
        response = self.client.get(
            self.report_article_url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.super_user)
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_report_admin_denied_2(self):
        self.report_data_2 = {
            "violation_report": "this is the report",
            "report_status": "dismissed",
            "violation_subject": "new"
        }
        self.client.force_authenticate(user=self.super_user)
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_report_status_admin(self):
        self.report_data_2 = {"report_status": "allegations_false"}
        self.client.force_authenticate(user=self.super_user)
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_report_non_admin_success(self):
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_report_non_admin_failed(self):
        self.client.force_authenticate(user=self.super_user)
        new_status = {"report_status": "allegations_true"}
        self.client.put(
            self.report_article_url, data=new_status, format='json'
        )
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_report_non_admin_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.report_article_url, data=self.report_data_2, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
