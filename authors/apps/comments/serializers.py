from rest_framework import serializers
from .models import (Comment,CommentLikeDislike)
from authors.apps.profiles.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    """ Converts Comment data into  one that can then be easily rendered into JSON"""

    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
                "id", 
                "created_at", 
                "updated_at", 
                "body", 
                "author",
                "highlighted_text",
                "start_index",
                "end_index",
            )
        read_only = ("article", "author", "created_at", "updated_at")


class CommentLikesDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLikeDislike
        fields = '__all__'
        read_only_fields = ['comment', 'user']