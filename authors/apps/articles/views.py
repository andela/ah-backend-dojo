from django.shortcuts import (
                              get_object_or_404, 
                              get_list_or_404)
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import (generics, 
                            response, 
                            status)
from django.utils import timezone
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        AllowAny
                                        )
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article, FavoriteArticle
from .serializers import (ArticleSerializer,
                           FavoriteArticleSerializer)
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User

class Articles(APIView):
    #Route protection
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        articles = Article.objects.all().order_by('createdAt')
        serializer = ArticleSerializer(articles, many=True)
        articles_count = len(serializer.data)
        all_articles = serializer.data
        articles_list = []
        for article in all_articles:
            del article['id']
            articles_list.append(article)
        return Response({"articles": articles_list, "articlesCount": articles_count}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data.get('article', {})
        current_user = request.user
        data["slug"] = slugify(data["title"])
        data["author"] = current_user.username
        last_article = Article.objects.last()
        article_serializer = ArticleSerializer(last_article, many=False)
        last_article = article_serializer.data
        if Article.objects.filter(slug=data["slug"]).first():
            data["slug"] = "{}-{}".format(data["slug"], last_article['id']+1)
        serializer = ArticleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            article = serializer.data
            del article['id']
            return Response({"article": article}, status.HTTP_201_CREATED)
        return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

class OneArticle(APIView):
    #Route protection
    permission_classes = (IsAuthenticated,)

    def get(cls, request, article_id):
        article = get_object_or_404(Article, id=article_id, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        an_article = dict(serializer.data)
        del an_article['id']
        return Response({"article": an_article}, status=status.HTTP_200_OK)
    
    def put(cls, request, article_id):
        article = get_object_or_404(Article, id=article_id, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        json_data = request.data
        json_data = request.data["article"]
        data = dict(serializer.data)
        data["updatedAt"] = timezone.now()
        data["slug"] = data["title"]
        data["title"] = json_data.get("title")
        data["body"] = json_data.get("body")
        data["description"] = json_data.get("description")
        serializer = ArticleSerializer(article, data)
        if serializer.is_valid():
            serializer.save()
            article = serializer.data
            del article['id']
            return Response({"article": article}, status=status.HTTP_200_OK)
        return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(cls, request, article_id):
        article = get_object_or_404(Article, pk=article_id, delete_status=False)
        article.delete()
        return Response({"messege": "article deleted successfully"}, status=status.HTTP_200_OK)

class FavoriteArticleCreate(generics.ListCreateAPIView):
    """If the user feels satisfied with the article, he can favourite it """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = FavoriteArticleSerializer
    article_serializer_class = ArticleSerializer

    def check_article_exists(self, **kwargs):
        """
        Check whether article exists
        """
        article = get_object_or_404(
            Article, 
            slug=kwargs.get('slug')
        )
        return article

    def post(self, request, **kwargs):
        """
        Favorite an article
        """
        article = self.check_article_exists(**kwargs)
        favorite = FavoriteArticle.objects.filter(
            favorited_by=request.user, 
            article=article
        )
        if not favorite:
            serializer = self.serializer_class(data={'favorited':True})
            serializer.is_valid(raise_exception=True)
            serializer.save(
                article=article,
                favorited_by=request.user
            )
            return Response(
                {"message": "You have successfully favorited this article "},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "You already favorited this article"},
            status=status.HTTP_200_OK
        )


class UnFavoriteArticleDestroy(generics.DestroyAPIView):
    """If he feels disatisfied with the article he can Unfavourite it. """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = FavoriteArticleSerializer
    def delete(self, request, **kwargs):
        """
        Unfavorite an article
        """
        queryset = FavoriteArticle.objects.filter(favorited_by=request.user)
        favorited = queryset.filter(article_id=(Article.objects.filter(slug=kwargs.get('slug')).first()).id).first()
        serializer = FavoriteArticleSerializer(favorited)

        if not favorited:
            return Response(
                {
                    'message': "You have already unfavourited this article"
                }, status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(favorited)
        return Response(
            {
                "message": "You have successfully unfavorited this article."
            }, status.HTTP_200_OK)