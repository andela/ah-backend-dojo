from rest_framework import serializers
from .models import Article
from authors.apps.authentication.serializers import UserSerializer
from . import models

class ArticleSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    class Meta:
        fields = [
            'id',
            'slug',
            'title',
            'body',
            'description',
            'author',
            'publish_status',
            'createdAt',
            'updatedAt',
            'delete_status'
        ]
        read_only_fields = [
            ''
        ]
        model = Article

class FavoriteArticleSerializer(serializers.ModelSerializer):
    """
    Favorite Article serializer
    """
    article = ArticleSerializer(required=False)
    favorited_by = UserSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = models.FavoriteArticle
        read_only_fields = ['favorited_by', 'article']