from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    hello_authors_heaven,
    ActivateUserAccount,
)

# app_name = "authentication"

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('welcome/', hello_authors_heaven),
    path('users/activate/<uidb64>/<token>/',
            ActivateUserAccount.as_view(),
            name='activate_user_account')
]
