from django.urls import path, re_path, translate_url
from .views import (
    PostPostedList,
    PostUserPublishedList,
    stub_view,
    PostDetail,
    PostUserList,
    PostUserPublishedList,
    GenericSortedList,
    add_comment,
)

urlpatterns = [
    path("", PostPostedList.as_view(), name="post_index"),
    path("posts/<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("posts/<int:pk>/comments", add_comment, name="comments"),
    path("posts/<str:username>/", PostUserList.as_view(), name="post_user"),
    path(
        "posts/<str:username>/published/",
        PostUserPublishedList.as_view(),
        name="user_published",
    ),
    re_path(
        r"^posts/(?P<command>[A-Za-z]*)/(?P<parameter>[A-Za-z]*_?[A-Za-z]*?_?_?[A-Za-z]*)/(?P<value>[A-Za-z0-9]*|[0-9]{4}-[0-9]{2}-[0-9]{2})/$",
        GenericSortedList.as_view(),
        name="post_query",
    ),
]
