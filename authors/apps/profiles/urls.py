from django.urls import path
from .views import ProfileRetrieveUpdateView

app_name = "profiles"

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveUpdateView.as_view())
]
