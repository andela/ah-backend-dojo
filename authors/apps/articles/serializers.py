from rest_framework import serializers
from authors.apps.article_tag.models import ArticleTag
from .models import Article, FavoriteArticle
from authors.apps.authentication.serializers import UserSerializer

class ArticleSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    tagList = serializers.SlugRelatedField(
        many=True,
        queryset=ArticleTag.objects.all(),
        slug_field='tag_text'
    )
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
            'delete_status',
            'tagList'
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