from django.urls import path
from .views import NotificationViews

urlpatterns = [
    # /authors/followers/ or ../following/
    path("notifications/", NotificationViews.as_view(), name="notifications"),
    path("notify/", NotificationViews.as_view(), name="notifier"),
]