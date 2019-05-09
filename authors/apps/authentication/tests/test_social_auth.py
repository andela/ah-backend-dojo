from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User

class SocialTests(APITestCase):
    google_url = "/api/auth/google/"
    facebook_url = "/api/auth/facebook/"

    def setUp(self):

        self.valid_google_token = {
            "user": {
                "auth_token": "JhbGciOiJSUzI1NiIsImtpZCI6IjI4ZjU4MTNlMzI3YWQxNGNhYWYxYmYyYTEyMzY4NTg3ZTg4MmI2MDQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTQ0ODU5NzYwMTkwMzQ1MTE5MjQiLCJlbWFpbCI6Im11ZGlkaWppbW15QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiQTJlMC1sWko5MUstenIwaGo5UGJ6ZyIsIm5hbWUiOiJNdWRpZGkgSmFtZXMiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDUuZ29vZ2xldXNlcmNvbnRlbnQuY29tLy1Rb0pVZ20teWxmby9BQUFBQUFBQUFBSS9BQUFBQUFBQUZzNC94Rll2eWJ4Si1mcy9zOTYtYy9waG90by5qcGciLCJnaXZlbl9uYW1lIjoiTXVkaWRpIiwiZmFtaWx5X25hbWUiOiJKYW1lcyIsImxvY2FsZSI6ImVuIiwiaWF0IjoxNTU3MzI1ODU5LCJleHAiOjE1NTczMjk0NTl9.FF2tqXGG56xGb8NGqIxHaElWDnO0KJ3eY62e9Mn9D_FDYluedCfLPQEdWK6BL-Oxhu2YpXjxAaxDjdUuqtt3oheEsSi5FzWhwDuta1ZGh9iKR9gCd3T9Xbvcu7oy4ze7QDLJe4WV6vtOJPtRuV0xC5xGp4u8A_eatYH_qL5P5SnUisNhUrWGndjuxqaul_T53We9lK1Dxc9Ix1s79yecPl9o0EZFCwBYrg5cRt5Cuai6V3_j-9l78Bby4u9WxnmvmJ1XF9FT9NrbfJbhj3WFDi_6Nirmwpfdun4FDSEvXsi5s7d3j3uFJpGUoz9UcoVsHzY8uR8nNPrJdJqX-tKvZQ"
            }
        }

        self.valid_facebook_token = {
            "user": {
                "auth_token": "EAADZBFBOurzgBADvFoZCMD3PifgGcvc68cSogkfgabxs3iSnGoSamY6MEa3ZBP95cRhBSgzQSZAIyJLd75CJuSfwxvmDiCED1ZBDz2wfYGAeAMmSBKv4EKl99bMTjUINZCGlwB1giiwCyKJ14OXmezK88uwAHhhaEIyMdwPVVExty0a0qf0AAapNkNsrqL43HQWTVBjehtOQZDZD"
            }
        }

        self.invalid_token = {
            "user": {
                "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.\
                    eyJpZCI6NCwiaWF0IjoxNTU3MTM3MzQzLCJleHAiOjE1NTcxNDgx.\
                        Of40fTWM-Qadl0vM5nk-1wz30mU4kKjhXp_QHeAYl1M"
            }
        }

    
    # def test_valid_facebook_token(self):
    #     response = self.client.post(
    #         self.facebook_url, self.valid_facebook_token, format="json"
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("auth_token", response.data)
    
    def test_invalid_facebook_token(self):
        response = self.client.post(
            self.facebook_url, self.invalid_token, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            response.data["errors"]["auth_token"][0],
            "The token provided is invalid or has expired",
        )
    
    # def test_valid_google_token(self):
    #     response = self.client.post(
    #         self.google_url, self.valid_google_token, format="json"
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("auth_token", response.data)
    
    def test_invalid_google_token(self):
        response = self.client.post(
            self.google_url, self.invalid_token, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            response.data["errors"]["auth_token"][0],
            "The token provided is invalid or has expired",
        )
