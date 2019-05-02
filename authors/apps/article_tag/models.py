from django.db import models
from django.contrib.postgres.fields import ArrayField

class ArticleTag(models.Model):
    """Model for single tag"""
    tag_text = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.tag_text
