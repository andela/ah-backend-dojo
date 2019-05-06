from django.urls import path

from .views import CreateDestroyBookmarksView, ListBookmarksView

urlpatterns = [
    path(
        "articles/<str:slug>/bookmark/",
        CreateDestroyBookmarksView.as_view(),
        name="create_destroy_bookmarks",
    ),
    path("bookmarks/", ListBookmarksView.as_view(), name="get_bookmarks"),
]
