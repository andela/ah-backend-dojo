from django.db import models
from authors.apps.authentication.models import User

class AuthorFollowing(models.Model):
    follower = models.CharField(max_length=255)
    following = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)