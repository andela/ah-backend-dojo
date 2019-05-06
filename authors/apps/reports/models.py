from django.db import models
from authors import settings
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile

# Create your models here.
class ReportArticle(models.Model):
    """model for reporting an article"""
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, to_field="slug", on_delete=models.CASCADE)
    violation_subject = models.CharField(max_length=100, blank=False, null=False)
    violation_report = models.CharField(max_length=300, blank=True, null=True)
    report_status = models.CharField(max_length=20, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True, editable=False)

    