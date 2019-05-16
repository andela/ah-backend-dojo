import readtime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from authors.apps.article_tag.views import ArticleTagViewSet
from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import UserSerializer
from .extra_methods import create_slug
from .extra_methods import like_grand_count
from .mixins import CustomPaginationMixin
from .models import Article, FavoriteArticle, ReadingStats
from .serializers import (
    ArticleSerializer,
    FavoriteArticleSerializer,
    EmailSerializer,
)
from authors.apps.reports.models import ReportArticle
from .serializers import (
    ArticleSerializer,
    FavoriteArticleSerializer,
    EmailSerializer,
    SlugSerializer,
)
from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import UserSerializer


class ListCreateArticlesView(APIView, CustomPaginationMixin):
    """
    This deals with;
    1. Getting all articles from the db
    2. Creating/Adding a new article to the db
    """

    # Route protection
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    queryset = (
        Article.objects.all().filter(delete_status=False).order_by("createdAt")
    )
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("author", "tag", "title", "body")

    def get_queryset(self):
        queryset = self.queryset

        author = self.request.query_params.get("author", None)
        if author is not None:
            queryset = self.queryset.filter(author__username__icontains=author)

        tag = self.request.query_params.get("tag", None)
        if tag:
            queryset = queryset.filter(tagList__tag_text__icontains=tag)

        title = self.request.query_params.get("title", None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(author__username__icontains=search)
                | Q(title__icontains=search)
                | Q(tagList__tag_text__icontains=search)
                | Q(body__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset

    def get(self, request):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            articles_count = len(serializer.data)
            all_articles = serializer.data

            articles_list = []

            for article in all_articles:
                article["likeCount"] = [like_grand_count(article)]
                articles_list.append(article)
            return self.get_paginated_response(
                {
                    "articles": articles_list,
                    "articlesCount": articles_count,
                    "status": status.HTTP_200_OK,
                }
            )

    def post(self, request):
        data = request.data.get("article", {})
        current_user = request.user

        serializer = SlugSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        data["slug"] = create_slug(data["title"])
        data["author"] = current_user.username
        data["time_to_read"] = get_time_to_read(data.get("body"))

        """create tag if it doesn't exist"""
        tag_list = ArticleTagViewSet.create_tag_if_not_exist(
            ArticleTagViewSet, data.get("tagList")
        )
        data["tagList"] = tag_list

        serializer = ArticleSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        article = dict(serializer.data)
        article["likeCount"] = [like_grand_count(article)]

        return Response({"article": article}, status.HTTP_201_CREATED)


class RetrieveUpdateDeleteArticleView(APIView):
    """
    This deals with;
    1. Getting a single article from the db
    2. Updating a an article
    3. Deleting an article
    """

    # Route protection
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(cls, request, article_id):
        article = get_object_or_404(
            Article, id=article_id, delete_status=False
        )
        serializer = ArticleSerializer(article, many=False)
        an_article = dict(serializer.data)
        an_article["likeCount"] = [like_grand_count(an_article)]

        current_user = request.user
        # Make this functionality on available for logged in users.
        if (
            current_user.is_authenticated
            and article.author.username != current_user.username
        ):
            try:

                read_stats = ReadingStats.objects.create(
                    article=article, user=current_user, views=1, reads=0
                )

                read_stats.save()

            # If both user and article already exist, do nothing.
            except IntegrityError:
                pass

        return Response({"article": an_article}, status=status.HTTP_200_OK)

    def put(cls, request, article_id):
        article = get_object_or_404(
            Article, id=article_id, delete_status=False
        )
        serializer = ArticleSerializer(article, many=False)
        json_data = request.data
        current_user = request.user
        article_data = dict(serializer.data)
        author = article_data["author"]

        if current_user.username == author:
            json_data = request.data["article"]
            article_data["updatedAt"] = timezone.now()
            article_data["slug"] = create_slug(article_data["title"])
            article_data["title"] = json_data.get("title")
            article_data["body"] = json_data.get("body")
            article_data["description"] = json_data.get("description")
            article_data["time_to_read"] = get_time_to_read(
                json_data.get("body")
            )

            """create tag if it doesn't exist"""
            tag_list = ArticleTagViewSet.create_tag_if_not_exist(
                ArticleTagViewSet, json_data.get("tagList")
            )
            article_data["tagList"] = tag_list

            serializer = ArticleSerializer(article, article_data)

            if serializer.is_valid():
                serializer.save()
                article = dict(serializer.data)
                article["likeCount"] = [like_grand_count(article)]
                return Response(
                    {"article": article}, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"error": "you cannot edit an article created by another user"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def delete(cls, request, article_id):
        article = get_object_or_404(
            Article, id=article_id, delete_status=False
        )
        serializer = ArticleSerializer(article, many=False)
        current_user = request.user
        article_data = dict(serializer.data)
        author = article_data["author"]

        if current_user.username == author:
            article = get_object_or_404(
                Article, id=article_id, delete_status=False
            )
            article.delete()
            return Response(
                {"messege": "article deleted successfully"},
                status=status.HTTP_200_OK,
            )
        if current_user.is_superuser:
            try:
                reported_article = ReportArticle.objects.get(
                    article=article.slug, report_status="allegations_true"
                )
                article.delete_status = True
                article.save()
                return Response(
                    {
                        "message": "Reported article has been deleted successfully"
                    }
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "error": "No proof yet that this article has violated any terms of service"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        return Response(
            {"error": "you cannot delete an article created by another user"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class FavoriteArticleCreate(generics.ListCreateAPIView):
    """If the user feels satisfied with the article, he can favourite it """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = FavoriteArticleSerializer
    article_serializer_class = ArticleSerializer

    def check_article_exists(self, **kwargs):
        """
        Check whether article exists
        """
        article = get_object_or_404(Article, slug=kwargs.get("slug"))
        return article

    def post(self, request, **kwargs):
        """
        Favorite an article
        """
        article = self.check_article_exists(**kwargs)
        favorite = FavoriteArticle.objects.filter(
            favorited_by=request.user, article=article
        )
        if not favorite:
            serializer = self.serializer_class(data={"favorited": True})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article, favorited_by=request.user)
            return Response(
                {"message": "You have successfully favorited this article "},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "You already favorited this article"},
            status=status.HTTP_200_OK,
        )


class UnFavoriteArticleDestroy(generics.DestroyAPIView):
    """If he feels disatisfied with the article he can Unfavourite it. """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = FavoriteArticleSerializer

    def delete(self, request, **kwargs):
        """
        Unfavorite an article
        """
        queryset = FavoriteArticle.objects.filter(favorited_by=request.user)
        favorited = queryset.filter(
            article_id=(
                Article.objects.filter(slug=kwargs.get("slug")).first()
            ).id
        ).first()
        serializer = FavoriteArticleSerializer(favorited)

        if not favorited:
            return Response(
                {"message": "You have not favourited this article"},
                status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(favorited)
        return Response(
            {"message": "You have successfully unfavorited this article."},
            status.HTTP_200_OK,
        )


class ShareOnFaceBookView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        facebook_share_url = "https://www.facebook.com/sharer/sharer.php?u="
        return social_media_share(
            ShareOnFaceBookView, request, kwargs, facebook_share_url
        )


class ShareOnTwitterView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        twitter_share_url = "https://twitter.com/home?status="
        return social_media_share(
            ShareOnTwitterView, request, kwargs, twitter_share_url
        )


def social_media_share(self, request, kwargs, share_url):
    server_url = f"https://{get_current_site(request)}"
    articles_endpoint = "api/articles"
    share_link = (
        f"{server_url}/{articles_endpoint}/{kwargs.get('article_id')}/"
    )
    message = {"share_link": f"{share_url}{share_link}"}
    return Response(message)


class ShareEmailView(ModelViewSet):
    """creating links for sharing articles via facebook
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        article = Article.objects.get(id=self.kwargs.get("article_id"))
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        reciever_mail = serializer.data["email"]

        user_obj = User.objects.get(username=request.user.username)
        user_serializer = UserSerializer(user_obj)
        article_serializer = ArticleSerializer(article)
        article_id = article.id
        sender_email = request.user.email

        server_url = f"https://{get_current_site(request)}"
        articles_endpoint = "api/articles"
        email_share_url = f"{server_url}/{articles_endpoint}/{article_id}/"
        message = {"message": "Your article has been shared successfully"}
        article_data = article_serializer.data
        article_data["body"] = f"{article_data['body'][:300]} ..."
        share_article_email(
            user_serializer.data,
            article_data,
            sender_email,
            reciever_mail,
            email_share_url,
        )

        return Response(message)


def get_time_to_read(body):
    """
    Method to calculate the time to read
    """
    return readtime.of_text(body).minutes


def share_article_email(
    user, article, sender_email, receiver_email, article_link
):
    """
    Function that sends an email
    """
    text_content = "Account Activation Email"
    subject = f"Author's Haven: {article.get('title')}"
    template_name = "email_share_article.html"
    recipients = [receiver_email]

    context = {"user": user, "activate_url": article_link, "article": article}

    html_content = render_to_string(template_name, context)
    email = EmailMultiAlternatives(
        subject, text_content, sender_email, recipients
    )
    email.attach_alternative(html_content, "text/html")

    email.send()


class ArticleReadStatView(APIView):
    """
        post:
        Register a user's read for an article

    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, article_id):
        article = get_object_or_404(
            Article, id=article_id, delete_status=False
        )

        current_user = request.user
        # Make this functionality on available for logged in users who are not
        # the authors of the specific article.
        if article.author.username != current_user.username:
            read_stats = ReadingStats.objects.get_or_create(
                article=article, user=current_user
            )
            if read_stats[0].views == 1:
                return Response(
                    data={
                        "message": (
                            f"Your read statistics for article with id {article.id} "
                            "are already registered successfully"
                        )
                    },
                    status=status.HTTP_200_OK,
                )

            read_stats[0].views = 1
            read_stats[0].reads = 1
            read_stats[0].save()

            return Response(
                data={
                    "message": (
                        f"Your read statistics for article with id {article.id} "
                        "were registered successfully"
                    )
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            data={
                "message": (
                    f"Your Read statistics are not captured for an article you "
                    "authored"
                )
            },
            status=status.HTTP_200_OK,
        )
