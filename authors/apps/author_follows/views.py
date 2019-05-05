from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.author_follows.models import AuthorFollowing
from authors.apps.articles.extra_methods import author_stats

class FollowStatsViews(APIView):
    """
    This deals with;
    1. Getting all your followers
    2. Getting all authors you follow
    """
    #Route protection
    permission_classes = (IsAuthenticated,)

    def get(self, request, follow_state):
        current_user = request.user
        if follow_state in ["following", "followers"]:
            all_follow_data = []
            follow_data = ""
            follow_count = 0
            if follow_state=="following":
                follow_data = AuthorFollowing.objects.filter(
                    follower=current_user.username
                )
                follow_data = [(followed.following).username for followed in follow_data]
                follow_count = len(follow_data)

            if follow_state=="followers":
                follow_data = AuthorFollowing.objects.filter(
                    following=current_user
                )
                follow_data = [follows.follower for follows in follow_data]
                follow_count = len(follow_data)
            for author in follow_data:
                followed_user_details = {}
                followed_user_details["author_name"] = author
                followed_user_details["author_stats"] = author_stats(author)
                all_follow_data.append(followed_user_details)
            return Response(
                {
                    follow_state: follow_count,
                    "data": all_follow_data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Not found"},
            status=status.HTTP_404_NOT_FOUND
        )        

class AuthorFollowViews(APIView):
    """
    This deals with;
    1. Following an author
    2. Unfollowing an author
    """
    #Route protection
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        current_user = request.user
        check_author = get_object_or_404(User, username=username)
        if username!=current_user.username:
            author_to_follow = AuthorFollowing.objects.filter(
                follower=current_user.username,
                following=check_author
            ).first()
            if author_to_follow:
                author_to_follow.delete()
                return Response(
                    {"message": "you have unfollowed {}".format(username)},
                    status=status.HTTP_200_OK
                )
            following_data = AuthorFollowing.objects.create(
                follower=current_user.username,
                following=check_author
            )
            following_data.save()
            return Response(
                {"message": "you have followed {}".format(username)},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "you can not follow yourself"},
            status=status.HTTP_400_BAD_REQUEST
        )