from django.urls import path
from .views import list_view, detail_view, PollDetailView, PollListView

urlpatterns = [
    path("", PollListView.as_view(), name="poll_index"),
    path("polls/<int:pk>/", PollDetailView.as_view(), name="poll_detail"),
]
