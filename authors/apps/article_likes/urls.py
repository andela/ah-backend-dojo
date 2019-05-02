from django.urls import path
from .views import ArticleLikesDislikesViews

urlpatterns = [
    # /articles/slug/like_status/
    path("<str:like_status>", ArticleLikesDislikesViews.as_view(), name="liking")
]