import readtime

from django.shortcuts import (
    get_object_or_404,
    get_list_or_404
)
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import (generics,
                            response,
                            status)
from django.utils import timezone


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)

from .models import Article
from .serializers import ArticleSerializer
from .extra_methods import create_slug, like_grand_count
from .mixins import CustomPaginationMixin
from .extra_methods import create_slug
from authors.apps.article_tag.views import ArticleTagViewSet
from .models import Article, FavoriteArticle
from .serializers import ArticleSerializer, FavoriteArticleSerializer

from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User

class ListCreateArticlesView(APIView, CustomPaginationMixin):
    """
    This deals with;
    1. Getting all articles from the db
    2. Creating/Adding a new article to the db
    """

    # Route protection
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    queryset = Article.objects.all().order_by("createdAt")
    serializer_class = ArticleSerializer

    def get(self, request):
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            articles_count = len(serializer.data)
            all_articles = serializer.data

            articles_list = []

            for article in all_articles:
                article['likeCount'] = [like_grand_count(article)]
                articles_list.append(article)
            return self.get_paginated_response(
                {
                    "articles": articles_list,
                    "articlesCount": articles_count,
                    "status": status.HTTP_200_OK,
                }
            )

    def post(self, request):
        data = request.data.get("article", {})
        current_user = request.user

        data["slug"] = create_slug(Article, data["title"])
        data["author"] = current_user.username
        data["time_to_read"] = get_time_to_read(data.get('body'))

        """create tag if it doesn't exist"""
        tag_list = ArticleTagViewSet.create_tag_if_not_exist(ArticleTagViewSet, data.get('tagList'))
        data["tagList"] = tag_list

        serializer = ArticleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            article = dict(serializer.data)
            article['likeCount'] = [like_grand_count(article)]
            return Response({"article": article}, status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteArticleView(APIView):
    """
    This deals with;
    1. Getting a single article from the db
    2. Updating a an article
    3. Deleting an article
    """

    # Route protection
    permission_classes = (IsAuthenticated,)

    def get(cls, request, article_id):
        article = get_object_or_404(Article, id=article_id, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        an_article = dict(serializer.data)
        an_article['likeCount'] = [like_grand_count(an_article)]
        return Response({"article": an_article}, status=status.HTTP_200_OK)

    def put(cls, request, article_id):
        article = get_object_or_404(Article, id=article_id, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        json_data = request.data
        current_user = request.user
        article_data = dict(serializer.data)
        author = article_data["author"]

        if current_user.username == author:
            json_data = request.data["article"]
            article_data["updatedAt"] = timezone.now()
            article_data["slug"] = create_slug(Article, article_data['title'])
            article_data["title"] = json_data.get("title")
            article_data["body"] = json_data.get("body")
            article_data["description"] = json_data.get("description")
            article_data["time_to_read"] = get_time_to_read(json_data.get('body'))

            """create tag if it doesn't exist"""
            tag_list = ArticleTagViewSet.create_tag_if_not_exist(ArticleTagViewSet, json_data.get('tagList'))
            article_data["tagList"] = tag_list

            serializer = ArticleSerializer(article, article_data)

            if serializer.is_valid():
                serializer.save()
                article = dict(serializer.data)
                article['likeCount'] = [like_grand_count(article)]
                return Response({"article": article}, status=status.HTTP_200_OK)
            return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
                {"error":"you cannot edit an article created by another user"},
                status=status.HTTP_401_UNAUTHORIZED
        )

    def delete(cls, request, article_id):
        article = get_object_or_404(Article, id=article_id, delete_status=False)
        serializer = ArticleSerializer(article, many=False)
        current_user = request.user
        article_data = dict(serializer.data)
        author = article_data["author"]

        if current_user.username == author:
            article = get_object_or_404(Article, id=article_id, delete_status=False)
            article.delete()
            return Response({"messege": "article deleted successfully"}, status=status.HTTP_200_OK)
        return Response(
                {"error": "you cannot delete an article created by another user"},
                status=status.HTTP_401_UNAUTHORIZED
        )

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
            serializer = self.serializer_class(data={"favorited": True})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article, favorited_by=request.user)
            return Response(
                {"message": "You have successfully favorited this article "},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "You already favorited this article"},
            status=status.HTTP_200_OK,
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
        favorited = queryset.filter(
            article_id=(
                Article.objects.filter(slug=kwargs.get("slug")).first()
            ).id
        ).first()
        serializer = FavoriteArticleSerializer(favorited)

        if not favorited:
            return Response(
                {"message": "You have not favourited this article"},
                status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(favorited)
        return Response(
            {
                "message": "You have successfully unfavorited this article."
            },
            status.HTTP_200_OK
        )


def get_time_to_read(body):
    '''
    Method to calculate the time to read
    '''
    return readtime.of_text(body).minutes
