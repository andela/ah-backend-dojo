from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from .serializers import ArticleSerializer
from authors.apps.tag_article.views import ArticleTagViewSet
from authors.apps.tag_article.models import ArticleTag
from authors.apps.tag_article.serializers import ArticleTagSerializer

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

        self.create_tag_if_not_exist(data.get('article_tags'))

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

    def create_tag_if_not_exist(self, provided_tags):
        """method to create a tag if it doesn't exist"""
        my_article_tags = ArticleTag.objects.all()
        print(my_article_tags)
        
        try:
            for provided_tag in provided_tags:
                ArticleTag.objects.get(tag_text=provided_tag)
                
        except ObjectDoesNotExist:
            serializer = ArticleTagSerializer(data={"tag_text": provided_tag})
            serializer.is_valid(serializer)
            ArticleTagViewSet.perform_create(Articles,serializer)

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

                


