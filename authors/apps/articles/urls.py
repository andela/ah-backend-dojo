from django.urls import path

from authors.apps.articles.views import (
    ListCreateArticlesView,
    RetrieveUpdateDeleteArticleView,
    FavoriteArticleCreate,
    UnFavoriteArticleDestroy,
)

urlpatterns = [
    # /articles/
    path(
        "",
        ListCreateArticlesView.as_view(),
        name="articles"
    ),
    # /articles/123/
    path(
        "<int:article_id>/",
        RetrieveUpdateDeleteArticleView.as_view(),
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
    ),

]
