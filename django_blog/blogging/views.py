from django.shortcuts import render
from django.http import Http404
from .models import Post

def list_view(request):
    context = {'posts': Post.objects.all()}
    return render(request, 'blogging/list.html', context)


def detail_view(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404
    
    context = {'post': post}
    return render(request, 'blogging/detail.html', context)
