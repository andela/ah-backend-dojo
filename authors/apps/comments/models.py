from django.db import models
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Article


class Comment(models.Model):
    body = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.body

class CommentLikeDislike(models.Model):
    '''Make sure a user can like or dislike a comment '''

    like = models.BooleanField(default=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.like
