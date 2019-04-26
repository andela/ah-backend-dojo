from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.decorators import api_view, permission_classes

from drf_yasg.utils import swagger_auto_schema

from .renderers import UserJSONRenderer
from .models import User
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
)


@api_view()
@permission_classes((IsAuthenticated,))
def hello_authors_heaven(request):
    return Response({"message": "Hello, world!"})


class RegistrationAPIView(APIView):

    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_description="Regester a new User.",
        operation_id="Sign up as a new user",
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: "BAD REQUEST"},
    )
    def post(self, request):
        user = request.data.get("user", {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #send activation email
        uid = User.objects.get(email= user['email']).id
        user['id'] = uid
        send_account_activation_email(request, user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="Login a User.",
        operation_id="Login a user",
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: "BAD REQUEST"},
    )
    def post(self, request):
        user = request.data.get("user", {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    """
    retrieve:
    Get user details
    update:
    Edit user details
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_id="Retrieve User data",
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: "BAD REQUEST"},
    )
    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update User data.",
        request_body=UserSerializer,
        responses={201: UserSerializer(many=False), 400: "BAD REQUEST"},
    )
    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get("user", {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

def send_account_activation_email(request, user):
    '''
    Function that sends an email
    '''
    text_content = 'Account Activation Email'
    subject = "Author's Haven"
    template_name = "activation.html"
    recipients = [user['email']]
    uid = user['id']
    user_obj = User.objects.get(pk=uid)

    kwargs = {
        "uidb64": urlsafe_base64_encode(force_bytes(uid)).decode(),
        "token": default_token_generator.make_token(user_obj)
    }

    activation_url = reverse("activate_user_account", kwargs=kwargs)

    activate_url = "{0}://{1}{2}".format(request.scheme,
                    request.get_host(), activation_url)

    context = {
        'user': user,
        'activate_url': activate_url
    }

    html_content = render_to_string(template_name, context)
    email = EmailMultiAlternatives(subject, text_content,
            settings.EMAIL_HOST_USER, recipients)
    email.attach_alternative(html_content, "text/html")

    email.send()

class ActivateUserAccount(APIView):
    """
    Activate an account
    """
    def get(self, request, **kwargs):

        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)

        except User.DoesNotExist:
            return Response("Activation failed")

        if user and default_token_generator.check_token(user, kwargs['token']):
            user.is_email_verified = True
            user.is_active = True
            user.save()
            return Response("Activation successful")   
        else:
            return Response("Activation link has expired")         
