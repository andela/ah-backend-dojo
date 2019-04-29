from rest_framework import serializers
from .models import Article
from authors.apps.tag_article.models import ArticleTag

class ArticleSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""    
    article_tags = serializers.SlugRelatedField(
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
            'article_tags'
        ]
        read_only_fields = [
            ''
        ]
        model = Article
