from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article

class ArticleLike(models.Model):
    liked_by = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, to_field="id", on_delete=models.CASCADE)
    like_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)