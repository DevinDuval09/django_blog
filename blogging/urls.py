from django.urls import path, re_path
from .views import (
    PostPostedList,
    PostUserNotPublished,
    PostUserPublishedList,
    PostDetail,
    PostUserList,
    PostUserPublishedList,
    GenericSortedList,
    add_comment,
    create_user,
    create_post,
    edit_post,
)

urlpatterns = [
    path("", PostPostedList.as_view(), name="post_index"),
    path("posts/<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("posts/<int:pk>/comments/", add_comment, name="comments"),
    path("posts/<int:pk>/edit/", edit_post, name="edit_post"),
    path("posts/new_post/", create_post, name="create_post"),
    path("posts/<str:username>/", PostUserList.as_view(), name="post_user"),
    path(
        "posts/<str:username>/published/",
        PostUserPublishedList.as_view(),
        name="user_published",
    ),
    path(
        "posts/<str:username>/unpublished/",
        PostUserNotPublished.as_view(),
        name="user_not_published",
    ),
    re_path(
        r"^posts/(?P<command>[A-Za-z]*)/(?P<parameter>[A-Za-z]*_?[A-Za-z]*?_?_?[A-Za-z]*)/(?P<value>[A-Za-z0-9]*|[0-9]{4}-[0-9]{2}-[0-9]{2})/$",
        GenericSortedList.as_view(),
        name="post_query",
    ),
    path("register/", create_user, name="create_user"),
]
