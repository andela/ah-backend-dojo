from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User

class TestLogin(APITestCase):
    login_url = '/api/users/login/'
    signup_url = '/api/users/'

    def setUp(self):
        user_data = {
            "user": {
                "username": "janee",
                "email": "janee@bg.com",
                "password": "Simplepassword2"
            }
        }
        
        response = self.client.post(self.signup_url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_wrong_email(self):
        response = self.client.post(
            self.login_url, 
            data={'user':{'email':'jane@bg.com', 'password':'simplepassword'}}, 
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors')
        .get('error')[0], "A user with this email and password was not found.")

    def test_wrong_password(self):
        response = self.client.post(
            self.login_url, 
            data={'user':{'email':'janee@bg.com', 'password':'wrongpassword'}}, 
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors')
        .get('error')[0], "A user with this email and password was not found.")

    def test_empty_email(self):
        response = self.client.post(
            self.login_url, 
            data={'user':{'email':'', 'password':'simplepassword'}}, 
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors')
        .get('email')[0], "This field may not be blank.")

    def test_empty_email(self):
        response = self.client.post(
            self.login_url, 
            data={'user':{'email':'janee@bg.com', 'password':''}}, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors')
        .get('password')[0], "This field may not be blank.")


    def test_login_success(self):
        user = User.objects.get(email='janee@bg.com')
        user.is_active = True
        user.save()
        response = self.client.post(
            self.login_url, 
            data={'user':{'email':'janee@bg.com', 'password':'Simplepassword2'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    