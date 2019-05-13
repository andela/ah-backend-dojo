from rest_framework import serializers

from authors.apps.article_tag.models import ArticleTag
from authors.apps.authentication.serializers import UserSerializer
from .models import Article, FavoriteArticle
from .models import ReadingStats


class ArticleSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    tagList = serializers.SlugRelatedField(
        many=True,
        queryset=ArticleTag.objects.all(),
        slug_field='tag_text'
    )
    read_stats = serializers.SerializerMethodField()

    def get_read_stats(self, instance):
        read_results = ReadingStats.objects.all().filter(article=instance.id)
        views = read_results.filter(views=1).count()
        reads = read_results.filter(reads=1).count()

        return {
            "views": views,
            "reads": reads
        }

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
            'tagList',
            'time_to_read',
            'read_stats'
        ]
        model = Article
        read_only = ('read_stats',)


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


class ReadingStatsSerializer(serializers.ModelSerializer):
    """
    Reading stats serializer
    """

    class Meta:
        fields = ('article', 'user')
        model = ReadingStats

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email', ]
