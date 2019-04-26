from django.urls import path
from .views import Articles, OneArticle

urlpatterns = [
    # /articles/
    path("", Articles.as_view(), name="articles"),
    # /articles/123/
    path("<int:article_id>", OneArticle.as_view(), name="article"),
]