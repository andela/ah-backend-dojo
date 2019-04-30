from django.urls import path
from .views import ListCreateCommentView, UpdateDestroyCommentView

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
]
