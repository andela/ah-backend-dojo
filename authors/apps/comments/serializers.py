"""Module containing serializers relating to comments"""
from rest_framework import serializers
from authors.apps.profiles.serializers import ProfileSerializer
from .models import (Comment, CommentLikeDislike, CommentEditHistory)

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
    """Converts likes and dislikes data into json format"""
    class Meta:
        model = CommentLikeDislike
        fields = '__all__'
        read_only_fields = ['comment', 'user']

class CommentEditHistorySerializer(serializers.ModelSerializer):
    """Converts comment edit history data into json format"""
    class Meta:
        model = CommentEditHistory
        fields = '__all__'
