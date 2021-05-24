
from django.urls import path
from .views import PostPostedList, stub_view, PostDetail

urlpatterns = [
    path('', PostPostedList.as_view(), name="post_index"),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post_detail'),
]