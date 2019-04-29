from authors.apps.article_rating.models import ArticleRating
from rest_framework.serializers import HyperlinkedModelSerializer, ValidationError, PrimaryKeyRelatedField, CurrentUserDefault
from rest_framework import serializers

class ArticleRatingSerializer(HyperlinkedModelSerializer):
    """This serializer is for creating, editing and viewing article-rating(s)"""
    user = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    def validate_rating(self, rating):
        if rating < 1 or rating > 5:
            raise ValidationError("Article-rating should range from 1 to 5")
        return rating
    class Meta:
        model = ArticleRating
        fields = ('rating',  'user')
