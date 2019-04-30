from django.db import models
from authors.apps.authentication.models import User
from authors.apps.article_tag.models import ArticleTag

class Article(models.Model):
    slug = models.CharField(max_length=110, unique=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    publish_status = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)
    tagList = models.ManyToManyField(ArticleTag, related_name='articles')

    def __str__(self):
        return self.title

class FavoriteArticle(models.Model):
    """
    Model for favoriting Articles
    """
    favorited = models.BooleanField(default=False)
    favorited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)