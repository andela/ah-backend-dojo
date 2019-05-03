from django.urls import path
from .views import (ListCreateCommentView, UpdateDestroyCommentView,
                    LikeComment,DislikeComment)

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
         DislikeComment.as_view())
]
