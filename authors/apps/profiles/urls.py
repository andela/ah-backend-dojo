from django.urls import path
from .views import ProfileRetrieveUpdateView, ListProfiles

app_name = "profiles"

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveUpdateView.as_view()),
    path('profiles/', ListProfiles.as_view())
]
