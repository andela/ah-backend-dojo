from django.urls import path
from .views import FollowStatsViews, AuthorFollowViews

urlpatterns = [
    # /authors/followers/ or ../following/
    path("<str:follow_state>/", FollowStatsViews.as_view(), name="follows"),

    # /authors/<author_username>/follow
    path("<str:username>/follow/", AuthorFollowViews.as_view(), name="follow")
]