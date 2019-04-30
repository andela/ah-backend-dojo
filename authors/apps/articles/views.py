from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from .serializers import ArticleSerializer
from .extra_methods import create_slug

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