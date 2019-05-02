from rest_framework import serializers
from .models import ArticleLike

class ArticleLikeSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    class Meta:
        fields = [
            'liked_by',
            'article',
            'like_value',
            'created_at',
        ]
        model = ArticleLike

        