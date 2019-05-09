"""module containing url patterns for the comments app"""
from django.urls import path
from authors.apps.comments.views import (
    ListCreateCommentView, UpdateDestroyCommentView,
    LikeComment, DislikeComment, CommentHistoryViewSet
)

urlpatterns = [
    path(
        "comments/",
        ListCreateCommentView.as_view(),
        name="list_create_comment",
    ),
    path(
        "comments/<pk>/",
        UpdateDestroyCommentView.as_view(),
        name="retrieve_update_destroy",
    ),
    path('comments/<int:pk>/like',
         LikeComment.as_view()),
    path('comments/<int:pk>/dislike',
         DislikeComment.as_view()),
    path('comments/<int:pk>/history',
         CommentHistoryViewSet.as_view({"get": "list"}))
]
