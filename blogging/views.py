from django.db.models import query
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import Http404
from .models import Post
from django.db import transaction
from django.template import loader
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CommentForm


def stub_view(request, *args, **kwargs):
    body = "Stub View\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join([f"\t{arg}" for arg in args])
    if kwargs:
        body += "Kwargs:\n"
        body += "\n".join([f"\t{tup}" for tup in kwargs.items()])
    return HttpResponse(body, content_type="text/plain")


def add_comment(request, **kwargs):
    form = CommentForm(request.POST)
    if form.is_valid():
        model_instance = form.save(commit=False)
        model_instance.save()
        return redirect("/")
    else:
        form = CommentForm(initial={"post": kwargs["pk"], "author": request.user})
        return render(
            request,
            "blogging/comment.html",
            {"form": form, "post": Post.objects.get(pk=kwargs["pk"])},
        )


class PostListAllView(ListView):
    model = Post
    template_name = "blogging/list.html"


class PostPostedList(ListView):
    queryset = Post.objects.exclude(post_date=None).order_by("-post_date")
    template_name = "blogging/list.html"


class PostDetail(DetailView):
    queryset = Post.objects.exclude(post_date=None)
    template_name = "blogging/detail.html"


class PostUserList(ListView):
    template_name = "blogging/list.html"

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs["username"])


class PostUserPublishedList(ListView):
    template_name = "blogging/list.html"

    def get_queryset(self):
        return (
            Post.objects.filter(author__username=self.kwargs["username"])
            .exclude(post_date=None)
            .order_by("-post_date")
        )


class GenericSortedList(ListView):
    model = Post
    template_name = "blogging/list.html"

    def get_queryset(self):
        kwargs_dict = {self.kwargs["parameter"]: self.kwargs["value"]}
        return getattr(self.model.objects, self.kwargs["command"])(**kwargs_dict)
