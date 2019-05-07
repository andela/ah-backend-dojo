from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json
from authors.apps.authentication.models import User


class TestProfileViews(TestCase):
    def setUp(self):
        self.email = 'johndoe@gmail.com'
        self.username = 'johndoe'
        self.password = 'Johndoe3@'

        #Another user
        self.email2 = 'fieldmarshal@gmail.com'
        self.username2 = 'fieldmarshal'
        self.password2 = 'FieldMarshal@'
        # create a user
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        
        # create the second user
        self.user2 = User.objects.create_user(
            self.username2, self.email2, self.password2)

        # verify a user's account and save
        self.user.is_verified = True
        self.user.save()
        self.token = self.user.token

        # verify and save the second user
        self.user2.is_verified = True
        self.user2.save()
        self.token2 = self.user2.token


        self.data = {
            'user': {
                'username': self.username,
                'email': self.email,
                'password': self.password,
            }
        }

        self.valid_profile_data = {
            "profile": {
                "bio": "software developer1",
                "image": "http://127.0.0.1:8000/api/profiles/nadralia/nadra.jpg"
            }
         }

        self.test_client = APIClient()

    def tearDown(self):
        pass

    def test_get_profile(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 200)

    def test_get_profile_that_doesnt_exist(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format("yourusername"), HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 404)
    
    def test_unauthenticated_user_cannot_get_profile(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

    def test_can_get_profile_for_different_user(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format("fieldmarshal"), HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.username2)

    def test_list_profiles(self):
        response = self.test_client.get(
            "/api/profiles/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile_successfully(self):
        response = self.test_client.put(
            "/api/profiles/{}/".format(self.username),
                                   data=json.dumps(self.valid_profile_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"],
                         self.valid_profile_data["profile"]["bio"])
    
    def test_cannot_update_profile_when_unauthenticated(self):
        response = self.client.put("/api/profiles/{}/".format("fieldmarshal"),
                                   data=json.dumps(self.valid_profile_data),
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_cannot_update_profile_of_different_user(self):
        response = self.test_client.put(
                                     "/api/profiles/{}/".format("fieldmarshal"),
                                     data=json.dumps(self.valid_profile_data),
                                        content_type="application/json", 
                                       HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_profile_of_unexisting_user(self):
        response = self.test_client.put(
                                     "/api/profiles/{}/".format("zackatama"),
                                     data=json.dumps(self.valid_profile_data),
                                        content_type="application/json", 
                                       HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    