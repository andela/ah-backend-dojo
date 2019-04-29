from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from authors.apps.tag_article.models import ArticleTag
from authors.apps.tag_article.serializers import ArticleTagSerializer

class ArticleTagViewSet(ModelViewSet):
    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer
