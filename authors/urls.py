"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from authors.apps.article_tag.views import ArticleTagViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Authors Haven",
        default_version='v1',
        description=("A community of like minded authors "
                     "to foster inspiration and innovation "
                     "by leveraging the modern web."),
        license=openapi.License(name="Andela License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register("api/articles/mytags", ArticleTagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/', include('authors.apps.authentication.urls')),
    path('api/articles/', include('authors.apps.articles.urls'),name="article-app"),
    path('api/articles/', include('authors.apps.article_rating.urls')),
    path('api/articles/<str:slug>/', include('authors.apps.article_likes.urls')),
    path('api/articles/<slug>/', include('authors.apps.comments.urls')),
    path('api/authors/', include('authors.apps.author_follows.urls')),
    path('api/', include('authors.apps.article_bookmarks.urls')),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path('api/', include('authors.apps.profiles.urls')),
]
