from rest_framework.test import APITestCase, APIClient

class TestLogin(APITestCase):
    login_url = '/api/users/'

    def setUp(self):
        pass

    def test_wrong_email(self):
        response = self.client.post(self.login_url, data={'email':'ed@cd.com', 'password':'this'},
        format='json')
        self.assertEqual(response.status_code, 400)