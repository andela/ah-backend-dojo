from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("id", "user", "article", "bookmarked_on")

        validators = [
            UniqueTogetherValidator(
                queryset=Bookmark.objects.all(), fields=("user", "article")
            )
        ]

        extra_kwargs = {
            "user": {"write_only": True},
            "id": {"read_only": True},
        }
