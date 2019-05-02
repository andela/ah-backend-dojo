from rest_framework.serializers import ModelSerializer, SlugRelatedField
from authors.apps.articles.models import Article
from authors.apps.article_tag.models import ArticleTag

class ArticleTagSerializer(ModelSerializer):
    articles = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )

    class Meta:
        model = ArticleTag
        fields = ('tag_text', 'articles')
