from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from .serializers import CommentSerializer
from .models import Comment
from .permissions import IsOwnerOrReadOnly


class ListCreateCommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        comment = request.data

        # get the article or return a 404 error
        article = get_object_or_404(Article, slug=kwargs["slug"])

        # user the current Id pf user to get their Profile object
        current_user = request.user
        author = Profile.objects.get(user=current_user)
        serializer = self.serializer_class(
            data=comment, context=({"article": article})
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, author=author)
        return Response(
            data={"comment": serializer.data}, status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):
        """Get comments on an article"""
        # get the article or return a 404 error
        article = get_object_or_404(Article, slug=kwargs["slug"])
        queryset = Comment.objects.filter(article=article)
        serializer = self.serializer_class(queryset, many=True)
        comments = serializer.data

        return Response(
            data={"comments": comments, "commentsCount": len(comments)},
            status=status.HTTP_200_OK,
        )


class UpdateDestroyCommentView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_fields = ("slug", "pk")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"message": "Comment deleted Successfully"},
            status=status.HTTP_200_OK,
        )

    def perform_destroy(self, instance):
        instance.delete()
