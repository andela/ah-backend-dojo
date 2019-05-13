from django.urls import path

from authors.apps.articles.views import (
    ListCreateArticlesView,
    RetrieveUpdateDeleteArticleView,
    FavoriteArticleCreate,
    UnFavoriteArticleDestroy,
    ShareOnFaceBookView,
    ShareOnTwitterView,
    ShareEmailView,
    ArticleReadStatView
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
    path(
        '<int:article_id>/facebookshare/',
        ShareOnFaceBookView.as_view(),
        name='share_on_facebook'
    ),
    path(
        '<int:article_id>/twittershare/',
        ShareOnTwitterView.as_view(),
        name='share_on_twitter'
    ),
    path(
        '<int:article_id>/emailshare/',
        ShareEmailView.as_view({'post':'create'}),
        name='share_on_email'
    ),
    path(
        "<int:article_id>/read_stat/",
        ArticleReadStatView.as_view(),
        name="article-reads-stats"
    ),

]
