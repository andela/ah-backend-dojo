from django.urls import path
from authors.apps.articles.views import (
    Articles, 
    OneArticle,
    FavoriteArticleCreate,
    UnFavoriteArticleDestroy
)

urlpatterns = [
    # /articles/
    path(
        "", 
        Articles.as_view(), 
        name="articles"
    ),
    # /articles/123/
    path(
        "<str:slug>/", 
        OneArticle.as_view(), 
        name="article"
    ),
    path(
        '<str:slug>/favorite/',
        FavoriteArticleCreate.as_view(),
        name='favorite'
    ),
    path(
        '<str:slug>/unfavorite/',
        UnFavoriteArticleDestroy.as_view(),
        name='unfavorite'
    )

]