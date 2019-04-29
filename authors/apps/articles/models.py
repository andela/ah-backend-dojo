from django.db import models
from authors.apps.authentication.models import User

class Article(models.Model):
    slug = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    publish_status = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)

    def __str__(self):
        return self.title