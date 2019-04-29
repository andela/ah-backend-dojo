from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault, ValidationError
from authors.apps.articles.models import Article
from authors import settings

class ArticleRating(models.Model):
    """Model class for the Article-Rating"""
    rating = models.IntegerField(default=0,null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=False, null=True,related_name="articlerating")
    article = models.ForeignKey(Article, to_field="slug", on_delete=models.CASCADE)

    def __str__(self):
        return self.rating
