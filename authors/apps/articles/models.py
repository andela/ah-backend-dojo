from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from authors.apps.article_tag.models import ArticleTag
from authors.apps.authentication.models import User


class Article(models.Model):
    slug = models.CharField(max_length=110, unique=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(
        User, to_field="username", on_delete=models.CASCADE)
    publish_status = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)
    tagList = models.ManyToManyField(ArticleTag, related_name='articles')
    time_to_read = models.IntegerField(default=0)

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


class ReadingStats(models.Model):
    """
    Model for Reading statistics
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reads = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('article','user')

    def __str__(self):
        return f"{self.user} - {self.article}"
