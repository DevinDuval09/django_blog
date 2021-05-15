
from django.urls import path
from .views import list_view, detail_view, user_view, update_user_posts

urlpatterns = [
    path('', list_view, name="post_index"),
    path('<int:post_id>/', detail_view, name='post_detail'),
    path('<str:username>/', user_view, name='user_view'),
    path('<str:username>/<str:text>/', update_user_posts, name='update_user_posts'),
]