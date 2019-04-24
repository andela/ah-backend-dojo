import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Bearer"

    def authenticate(self, request):
        request.user = None

        authorization_header = authentication.get_authorization_header(
            request
        ).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        # silence errors for missing token authorization header since this functionality is shared
        # with functionality for generating token for login and registration  and functionality for
        # protecting routes in the application
        if not authorization_header:
            return None

        # The Authorization  header should only exactly two parts
        # the prefix and the token contain the prefix and the token
        # i.e Authorization: 'Bearer JWT_TOKEN'
        if len(authorization_header) == 1 or len(authorization_header) > 2:
            raise exceptions.AuthenticationFailed("Invalid Access Token")
            # return None
        prefix = authorization_header[0].decode("utf-8")
        token = authorization_header[1].decode("utf-8")

        # if the Authorization header is present but does not have the Bearer prefix
        if (
            len(authorization_header) == 2
            and JWTAuthentication.authentication_header_prefix != prefix
        ):
            raise exceptions.AuthenticationFailed(
                "Bearer Missing in Authorizarion header"
            )

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """Verifies the access token
            Return the user details and  his access token
        """

        active_user = self._decode_token(token)

        try:
            user = User.objects.get(pk=active_user["id"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "Invalid user Token, please register an account to acquire valid login credentials."
            )

        return (user, token)

    def _decode_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Access Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(
                "Error decoding access Token"
            )
        return payload
