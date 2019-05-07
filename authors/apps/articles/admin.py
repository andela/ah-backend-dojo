from django.contrib import admin

from .models import Article, FavoriteArticle, ReadingStats

# Register your models here.

admin.site.register(Article)
admin.site.register(FavoriteArticle)
admin.site.register(ReadingStats)
