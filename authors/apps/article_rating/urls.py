from django.urls import path
from authors.apps.article_rating.views import AverageArticleRatingViewSet, ArticleRatingViewSet

urlpatterns = [
    path(
        "<str:slug>/article-rating/<int:rating>/", 
        ArticleRatingViewSet.as_view({'post':'create'}), name="rating"
    ),
    path(
        "<str:slug>/article-rating/average/", 
        AverageArticleRatingViewSet.as_view({'get':'list'}), name="average-rating"
    ),
]
