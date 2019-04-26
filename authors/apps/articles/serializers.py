from rest_framework import serializers
from .models import Article

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
        