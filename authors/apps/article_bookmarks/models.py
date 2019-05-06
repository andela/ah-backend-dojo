from django.db import models

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User


class Bookmark(models.Model):
    user = models.ForeignKey(
        User, to_field="username", on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article, to_field="id", on_delete=models.CASCADE
    )
    bookmarked_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.article}"

    class Meta:
        unique_together = ("user", "article")
