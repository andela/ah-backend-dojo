from django.urls import path
from .views import Articles, OneArticle

urlpatterns = [
    # /articles/
    path("", Articles.as_view(), name="articles"),
    # /articles/slug/
    path("<str:slug>/", OneArticle.as_view(), name="article"),
]