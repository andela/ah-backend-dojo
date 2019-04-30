from rest_framework import serializers
from .models import Article, FavoriteArticle
from authors.apps.authentication.serializers import UserSerializer

class ArticleSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    class Meta:
        fields = [
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
        model = Article

class FavoriteArticleSerializer(serializers.ModelSerializer):
    """
    Favorite Article serializer
    """
    article = ArticleSerializer(required=False)
    favorited_by = UserSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = FavoriteArticle
        read_only_fields = ['favorited_by', 'article']