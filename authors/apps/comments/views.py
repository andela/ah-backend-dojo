from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAcceptable
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from .serializers import (CommentSerializer,
                            CommentLikesDislikeSerializer)
from .models import (Comment, CommentLikeDislike)
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

class LikeComment(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CommentLikeDislike.objects.all()
    serializer_class = CommentLikesDislikeSerializer

    def get(self, request, **kwargs):
        """Get all like counts"""
        comment = CommentLikeDislike.objects.filter(comment_id=kwargs['pk'])
        serializer = self.serializer_class(comment, many=True)
        return Response({
                         "likes": serializer.data,
                         "likesCount": len(serializer.data)
                        })

    def post(self, request, **kwargs):
        """Like a comment """
        current_user = request.user
        user = Profile.objects.get(user=current_user)
        user_id = user.id
        comment_id = kwargs['pk']
        liked_comment = CommentLikeDislike.objects.filter(like=True)
        liked_by = CommentLikeDislike.objects.filter(user_id=user_id)
        if liked_comment and liked_by:
            return Response(
                    data={"message": "You have already liked this comment"},
                    status=status.HTTP_200_OK,
                )

        like_data = request.data.get("like", {})
        serializer = self.serializer_class(data=like_data)
        serializer.is_valid(raise_exception=True)
        comment = Comment.objects.filter(id=comment_id).first()
        serializer.save(comment=comment, user=user)
        return Response({'message': 'You have liked this comment',
                                  'Data': serializer.data},
                                 status=status.HTTP_200_OK)


class DislikeComment(generics.DestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = CommentLikeDislike.objects.all()
    serializer_class = CommentLikesDislikeSerializer

    def delete(self, request, **kwargs):
        """
        Dislike Comment
        """
        current_user = request.user
        user = Profile.objects.get(user=current_user)
        user_id = user.id
        comment_id = kwargs['pk']
        queryset = CommentLikeDislike.objects.filter(user_id=user_id,
                                                    comment_id=comment_id).first()

        serializer = CommentLikesDislikeSerializer(queryset)
        comment_like_object = serializer.data
        if comment_like_object and comment_like_object['like'] == True:
            queryset.delete()
            return Response(
                    {
                        "message": "your like has been successfully revoked"
                    },
                    status.HTTP_200_OK
                )
        return Response(
                {"message": "You have not liked this comment"},
                status.HTTP_400_BAD_REQUEST,
            )