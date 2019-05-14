from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    hello_authors_heaven,
    ActivateUserAccount,
    PasswordResetView,
)


urlpatterns = [
    path("user/", UserRetrieveUpdateAPIView.as_view()),
    path("users/", RegistrationAPIView.as_view()),
    path("users/login/", LoginAPIView.as_view()),
    path("welcome/", hello_authors_heaven),
    path(
        "users/activate/<uidb64>/<token>/",
        ActivateUserAccount.as_view(),
        name="activate_user_account",
    ),
    path('password_reset/',
        include('django_rest_passwordreset.urls',
        namespace='password_reset')
    ),
    
    path(
        "reset-password/<token>",
        PasswordResetView.as_view(),
        name="password_reset_verify_token",
    ),

    path('oauth/', include('social_django.urls', namespace='social')),
]
