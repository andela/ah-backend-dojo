from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authors.apps.articles.models import Article
from authors.apps.article_rating.models import ArticleRating
from authors.apps.article_rating.serializers import ArticleRatingSerializer

class AverageArticleRatingViewSet(ModelViewSet):
    """Endpoint for getting the average rating of a given article"""
    permission_classes = (IsAuthenticated,)
    queryset = ArticleRating.objects.all()
    serializer_class = ArticleRatingSerializer

    def list(self, request, slug):
        article = Article.objects.get(slug=slug)
        queryset = ArticleRating.objects.all().filter(article=article)
        serializer = ArticleRatingSerializer(queryset, many=True,context={'request': request})
        average = queryset.aggregate(Avg('rating'))
        return Response({"article": article.title, "average_rating": average.get("rating__avg")})


class ArticleRatingViewSet(ModelViewSet):
    """Api endpoint for adding, editting and viewing article ratings"""
    permission_classes = (IsAuthenticated,)
    queryset =  ArticleRating.objects.all()
    serializer_class = ArticleRatingSerializer

    def create(self, request, *args, **kwargs):
        article = Article.objects.get(slug=self.kwargs.get("slug"))
        serializer = self.get_serializer(data={"rating": self.kwargs.get("rating")})

        if article.author == self.request.user:
            return Response({
                "error": "You are not allowed to rate your own article" 
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            article_rating = ArticleRating.objects.get(user=self.request.user, article=article)
            serializer = self.get_serializer(article_rating, data={"rating": self.kwargs.get("rating")})
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {"message": "You have successfully updated the rating of the article"},
                    status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            self.perform_create(serializer)
            return Response({"message": "You have successfully rated the article"},
             status=status.HTTP_201_CREATED
            )
    

    def perform_create(self, serializer):
        article = Article.objects.get(slug=self.kwargs.get("slug"))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, article=article)

    def perform_update(self, serializer):
        serializer.save()
