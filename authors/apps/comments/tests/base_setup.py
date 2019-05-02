import json
from django.test import TestCase
from rest_framework.test import APIClient
from ..models import Comment
from django.contrib.auth import get_user_model
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from django.utils.text import slugify
from authors.apps.articles.extra_methods import create_slug


class BaseCommentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username="kalsmic",
            password="Pa$$word234",
            is_active=True,
            is_email_verified=True,
        )

        self.user2 = get_user_model().objects.create(
            username="arthur",
            password="Pa$$word234",
            email="email@email.arthur",
            is_active=True,
            is_email_verified=True,
        )

        self.article = Article.objects.create(
            title="Article 1 title",
            body="Article body",
            description="Article description",
            author=self.user,
            slug=create_slug(Article, "Article 1 title"),
        )
        self.profile = Profile.objects.get(user=self.user)

        self.comment = Comment.objects.create(
            body="My first comment", author=self.profile, article=self.article
        )
        self.client = APIClient()
