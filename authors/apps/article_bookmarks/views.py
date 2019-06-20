from os import environ

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.article_bookmarks.models import Bookmark
from authors.apps.article_bookmarks.serializers import BookmarkSerializer
from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticleSerializer


class CreateDestroyBookmarksView(APIView):
    """
        post:
        Bookmark or unbookmark an article
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        current_user = request.user
        slug = kwargs["slug"]
        try:
            article = get_object_or_404(Article, slug=slug)

            bookmark = Bookmark.objects.create(
                user=current_user, article=article
            )
            bookmark.save()
            serializer = BookmarkSerializer(bookmark)

        except IntegrityError:
            bookmark = Bookmark.objects.get(user=current_user, article=article)
            bookmark.delete()
            return Response(
                data={"message": "Article has been unBookmarked Successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            data={
                "message": "Article Bookmarked Successfully",
                "bookmark": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class RetrieveBookmarkStatusView(APIView):
    """
        get:
        Get the status of a user's article bookmark
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = request.user
        slug = kwargs["slug"]

        article = get_object_or_404(Article, slug=slug)

        # get bookmarks for this user and article
        user_bookmarks = Bookmark.objects.filter(
            user=request.user.username,
            article=article.id
        )

        bookmarked = False

        if len(user_bookmarks) > 0:
            bookmarked = True

        return Response(
            data={
                "isBookmarked": bookmarked,
            },
            status=status.HTTP_200_OK,
        )


class ListBookmarksView(APIView):
    """
        get:
        returns a list of bookmarks
    """

    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Returns a list of bookmarks that belong to the current user"""
        user_bookmarks = self.queryset.filter(user=self.request.user.username)
        serializer = BookmarkSerializer(user_bookmarks, many=True)
        bookmarks = serializer.data
        count = len(bookmarks)
        # Customize the bookmark response to include the url for article detail
        for bookmark in bookmarks:
            article_id = bookmark["article"]
            article = Article.objects.get(id=article_id)

            # change the bookmark data type from int to dictionary
            bookmark["article"] = {}
            article = ArticleSerializer(article).data
            bookmark["article"]["id"] = article_id
            bookmark["article"]["title"] = article["title"]
            bookmark["bookmarked_on"] = bookmark["bookmarked_on"]
            bookmark["article"][
                "url"
            ] = f"{environ.get('WEB_HOST')}/api/articles/{article_id}/"

        return Response(
            data={"bookmarks": bookmarks, "count": count},
            status=status.HTTP_200_OK,
        )
