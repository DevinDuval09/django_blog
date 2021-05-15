from django.shortcuts import render
from django.http import Http404
from .models import Post
from django.db import transaction

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

def user_view(request, username):
    
    posts = Post.objects.all().filter(author__username=username)
    
    context = {'posts': posts}
    print(context)
    return render(request, 'blogging/list.html', context)

def update_user_posts(request, username, text):
    #print(request)
    posts = Post.objects.all().select_for_update().filter(author__username=username)
    with transaction.atomic():
        try:
            assert len(posts) > 0
            for post in posts:
                post.text = text
                post.save()
        except AssertionError:
            raise transaction.TransactionManagementError(f'{username} does not have any posts.')
    
    context = {'posts': posts, 'username': username}
    return render(request, 'blogging/detail_list.html', context)

