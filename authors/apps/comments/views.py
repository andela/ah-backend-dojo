from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAcceptable
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .utils import validateData
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
        comment = request.data.get('comment', {})

        # get the article or return a 404 error
        article = get_object_or_404(Article, slug=kwargs["slug"])

        # user the current Id pf user to get their Profile object
        current_user = request.user
        author = Profile.objects.get(user=current_user)

        end_index = comment.get('end_index', 0)
        start_index = comment.get('start_index', 0)
        if "start_index" in comment and "end_index" in comment:
            is_data_valid = validateData(end_index,start_index,article)
            if is_data_valid == True:
                #get the exact hightlighted value
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

        return Response({"comment": comment_data},
                                 status=status.HTTP_201_CREATED)

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
                data={"message": "Your comment is not new, make sure you change the comment body"}, 
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                        "message": "Your like has been successfully revoked"
                    },
                    status.HTTP_200_OK
                )
        return Response(
                {"message": "You have not liked this comment"},
                status.HTTP_400_BAD_REQUEST,
            )