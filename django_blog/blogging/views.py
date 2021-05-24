from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import Http404
from .models import Post
from django.db import transaction
from django.template import loader
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

def stub_view(request, *args, **kwargs):
    body = "Stub View\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join([f'\t{arg}' for arg in args])
    if kwargs:
        body += "Kwargs:\n"
        body += '\n'.join([f'\t{key}: {value}' for key, value in kwargs.items()])
    return HttpResponse(body, content_type='text/plain')


class PostListAllView(ListView):
    model = Post
    template_name = 'blogging/list.html'


class PostPostedList(ListView):
    queryset = Post.objects.exclude(post_date=None).order_by('-post_date')
    template_name = 'blogging/list.html'


class PostDetail(DetailView):
    queryset = Post.objects.exclude(post_date=None)
    template_name = 'blogging/detail.html'

            


