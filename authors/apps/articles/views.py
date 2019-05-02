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
from .extra_methods import create_slug
from authors.apps.article_tag.views import ArticleTagViewSet
from .models import Article, FavoriteArticle
from .serializers import (ArticleSerializer,
                           FavoriteArticleSerializer)
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User

class Articles(APIView):
    """
    This deals with;
    1. Getting all articles from the db
    2. Creating/Adding a new article to the db
    """
    #Route protection
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        articles = Article.objects.all().order_by('createdAt')
        serializer = ArticleSerializer(articles, many=True)
        articles_count = len(serializer.data)
        all_articles = serializer.data
        articles_list = []
        for article in all_articles:
            articles_list.append(article)
        return Response({"articles": articles_list, "articlesCount": articles_count}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data.get('article', {})
        current_user = request.user
        data["slug"] = create_slug(Article, data['title'])
        data["author"] = current_user.username

        """create tag if it doesn't exist"""
        tag_list = ArticleTagViewSet.create_tag_if_not_exist(ArticleTagViewSet, data.get('tagList'))
        data["tagList"] = tag_list
        serializer = ArticleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            article = serializer.data
            return Response({"article": article}, status.HTTP_201_CREATED)
        return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

class OneArticle(APIView):
    """
    This deals with;
    1. Getting a single article from the db
    2. Updating a an article
    3. Deleting an article
    """
    #Route protection
    permission_classes = (IsAuthenticated,)

    def get(cls, request, slug):
        article = get_object_or_404(Article, slug=slug, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        an_article = dict(serializer.data)
        return Response({"article": an_article}, status=status.HTTP_200_OK)
    
    def put(cls, request, slug):
        article = get_object_or_404(Article, slug=slug, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        json_data = request.data
        json_data = request.data["article"]
        data = dict(serializer.data)
        data["updatedAt"] = timezone.now()
        data["slug"] = create_slug(Article, data['title'])
        data["title"] = json_data.get("title")
        data["body"] = json_data.get("body")
        data["description"] = json_data.get("description")

        """create tag if it doesn't exist"""
        tag_list = ArticleTagViewSet.create_tag_if_not_exist(ArticleTagViewSet, json_data.get('tagList'))
        data["tagList"] = tag_list

        serializer = ArticleSerializer(article, data)
        if serializer.is_valid():
            serializer.save()
            article = serializer.data
            return Response({"article": article}, status=status.HTTP_200_OK)
        return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(cls, request, slug):
        article = get_object_or_404(Article, slug=slug, delete_status=False)
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
                    'message': "You have not favourited this article"
                }, status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(favorited)
        return Response(
            {
                "message": "You have successfully unfavorited this article."
            }, status.HTTP_200_OK)