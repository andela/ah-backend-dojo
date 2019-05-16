'''
This module contains handlers for social authentication
'''
import facebook
from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from .models import User


def register_social_user(email, username):
    '''
    This function handles user registration
    and user login
    '''
    user = User.objects.filter(email=email)
    password = User.objects.make_random_password(length=20)

    if user.exists():
        current_user = User.objects.get(email=email)
        return current_user.token

    else:
        user = {
            'username': username, 'email': email, 'password': password}
        new_user = User.objects.create_user(**user)
        new_user.is_active = True
        new_user.save()
        new_social_user = authenticate(email=email, password=password)
        return new_social_user.token


class GoogleHandler:
    '''Here we are creating a class that will help us
    handle the user information got from google'''

    @staticmethod
    def validate(auth_token):
        '''At this point of the GoogleHandler class we are
        Getting and Validating the user information from
        the authorization token'''

        try:
            id_info = id_token.verify_oauth2_token(
                auth_token, requests.Request())
            return id_info
        except Exception:
            return "The token provided is invalid or has expired"


class FacebookHandler:
    '''Here we are creating a class that will help us
    handle the user information got from facebook'''

    @staticmethod
    def validate(auth_token):
        '''At this point of the FacebookHandler class we are
        Getting and Validating the user information from
        the authorization token'''

        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=id,name,email')
            return profile
        except Exception:
            return "The token provided is invalid or has expired"
