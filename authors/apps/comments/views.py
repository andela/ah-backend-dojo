from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from .utils import validateData

from .serializers import (
    CommentSerializer,
    CommentLikesDislikeSerializer,
    CommentEditHistorySerializer
)
from .models import (Comment, CommentLikeDislike, CommentEditHistory)
from .permissions import IsOwnerOrReadOnly


class ListCreateCommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def post(self, request, **kwargs):
        comment = request.data.get('comment', {})

        # get the article or return a 404 error
        article = get_object_or_404(Article, slug=kwargs["slug"])

        # user the current Id pf user to get their Profile object
        current_user = request.user
        author = Profile.objects.get(user=current_user)

        end_index = comment.get('end_index', 0)
        start_index = comment.get('start_index', 0)
        if "start_index" in comment and "end_index" in comment:
            is_data_valid = validateData(end_index, start_index, article)
            if is_data_valid == True:
                # get the exact hightlighted value
                article_section = article.body[start_index:end_index]
                comment['highlighted_text'] = article_section
            else:
                return is_data_valid

        serializer = self.serializer_class(
            data=comment, context=({"article": article})
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, author=author)
        if "start_index" in comment and "end_index" in comment:
            comment_data = serializer.data
        else:
            comment_data = {
                "created_at": serializer.data['created_at'],
                "updated_at": serializer.data['updated_at'],
                "author": serializer.data['author'],
                "body": serializer.data['body'],
                "id": serializer.data['id']
            }

        return Response(
            {"comment": comment_data}, status=status.HTTP_201_CREATED
        )

    def get(self, request, **kwargs):
        """Get comments on an article"""
        # get the article or return a 404 error
        article = get_object_or_404(Article, slug=kwargs["slug"])
        queryset = Comment.objects.filter(article=article)
        serializer = self.serializer_class(queryset, many=True)
        comments = serializer.data
        new_comment_lists = []
        for comment in comments:
            likeStatus = False
            dislikeStatus = False
            try:
                current_user = request.user
                user = Profile.objects.get(user=current_user)
                user_id = user.id
                comment_id = comment.get("id")
                commentLikeState = CommentLikeDislike.objects.get(
                    comment_id=comment_id, user_id=user_id)
                serializer = CommentLikesDislikeSerializer(commentLikeState, many=False)
                likeStatus = serializer.data.get("like")
                dislikeStatus = (not likeStatus)
            except ObjectDoesNotExist:
                likeStatus = False
                dislikeStatus = False
            
            comment["likeStatus"] = likeStatus
            comment["dislikeStatus"] = dislikeStatus

        return Response(
            data={"comments": comments, "commentsCount": len(comments)},
            status=status.HTTP_200_OK,
        )

class UpdateDestroyCommentView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_fields = ("slug", "pk")

    def destroy(self, request, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"message": "Comment deleted Successfully"},
            status=status.HTTP_200_OK,
        )

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, slug, pk):
        """
        Function to edit comment body not the highlighted text
        """
        comment_data = get_object_or_404(Comment, pk=pk)
        article = get_object_or_404(Article, pk=comment_data.article.pk)
        user_profile = Profile.objects.get(user=request.user)
        update_data = request.data.get('comment', {})

        end_index = update_data.get('end_index', 0)
        start_index = update_data.get('start_index', 0)

        if "start_index" in update_data and "end_index" in update_data:
            return Response(
                data={"message": "You cannot edit the highlighted text"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if comment_data.author != user_profile:
            return Response(
                data={"message": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(comment_data, data=update_data,
                                           partial=True, context={"article": article})
        serializer.is_valid(raise_exception=True)
        if comment_data.body == update_data["body"]:
            return Response(
                data={
                    "message": "Your comment is not new, make sure you change the comment body"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        edited_comment = update_data["body"]
        comment_history_data = {
            "edited_comment": edited_comment, "original_comment": pk}
        comment_history_serilizer = CommentEditHistorySerializer(
            data=comment_history_data)
        comment_history_serilizer.is_valid(raise_exception=True)
        comment_history_serilizer.save()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeCommentStatus(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CommentLikeDislike.objects.all()
    serializer_class = CommentLikesDislikeSerializer

    def get(self, request, **kwargs):
        """Get the like state for a particular aunthenticated user"""
        try:
            current_user = request.user
            user = Profile.objects.get(user=current_user)
            user_id = user.id
            comment_id = kwargs['pk']
            comment = CommentLikeDislike.objects.get(
                comment_id=comment_id, user_id=user_id)
            serializer = self.serializer_class(comment, many=False)
            return Response({
                "status": serializer.data.get("like")
            })
        except ObjectDoesNotExist:
            return Response({
                "status": "none",
            })


class LikeComment(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CommentLikeDislike.objects.all()
    serializer_class = CommentLikesDislikeSerializer

    def get(self, request, **kwargs):
        """Get all like counts"""
        comment = CommentLikeDislike.objects.filter(
            comment_id=kwargs['pk'], like=True)
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
        try:
            mylike = CommentLikeDislike.objects.get(
                comment_id=comment_id, like=True, user_id=user_id)
            mylike.delete()
            return Response(
                data={
                    "message": "You have successfully revoked your like on this comment"},
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            try:
                mylike = CommentLikeDislike.objects.get(
                    comment_id=comment_id, like=False, user_id=user_id)
                mylike.like = True
                mylike.save()
                return Response(
                    data={"message": "You now like this comment"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                like_data = request.data.get("like", {})
                serializer = self.serializer_class(data=like_data)
                serializer.is_valid(raise_exception=True)
                comment = Comment.objects.filter(id=comment_id).first()
                serializer.save(comment=comment, user=user)
                return Response(
                    data={"message": "You have successfully liked this comment"},
                    status=status.HTTP_200_OK,
                )

class DislikeComment (generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CommentLikeDislike.objects.all()
    serializer_class = CommentLikesDislikeSerializer

    def get(self, request, **kwargs):
        """Get all like counts"""
        comment = CommentLikeDislike.objects.filter(
            comment_id=kwargs['pk'], like=False)
        serializer = self.serializer_class(comment, many=True)
        return Response({
            "dislikes": serializer.data,
            "dislikesCount": len(serializer.data)
        })

    def post(self, request, **kwargs):
        """Like a comment """
        current_user = request.user
        user = Profile.objects.get(user=current_user)
        user_id = user.id
        comment_id = kwargs['pk']
        try:
            mylike = CommentLikeDislike.objects.get(
                comment_id=comment_id, like=False, user_id=user_id)
            mylike.delete()
            return Response(
                data={
                    "message": "You have successfully revoked your dislike on this comment"},
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            try:
                mylike = CommentLikeDislike.objects.get(
                    comment_id=comment_id, like=True, user_id=user_id)
                mylike.like = False
                mylike.save()
                return Response(
                    data={"message": "You now dislike this comment"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                like_data = {"like": False}
                serializer = self.serializer_class(data=like_data)
                serializer.is_valid(raise_exception=True)
                comment = Comment.objects.filter(id=comment_id).first()
                serializer.save(comment=comment, user=user)
                return Response(
                    data={"message": "You have successfully disliked this comment"},
                    status=status.HTTP_200_OK,
                )


class CommentHistoryViewSet(ModelViewSet):
    """View for viewing the list of comment edit history"""
    queryset = CommentEditHistory.objects.all().order_by("edited_time")
    serializer_class = CommentEditHistorySerializer

    def list(self, request, **kwargs):
        try:
            Article.objects.get(slug=kwargs.get("slug"))
            Comment.objects.get(id=kwargs.get("pk"))
            queryset = CommentEditHistory.objects.all().filter(
                original_comment=kwargs.get("pk"))
            serializer = CommentEditHistorySerializer(
                queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "Article or comment doesn't exist"},
                            status=status.HTTP_404_NOT_FOUND
                            )
