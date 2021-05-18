from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import Http404
from .models import Post
from django.db import transaction
from django.template import loader

def stub_view(request, *args, **kwargs):
    body = "Stub View\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join([f'\t{arg}' for arg in args])
    if kwargs:
        body += "Kwargs:\n"
        body += '\n'.join([f'\t{key}: {value}' for key, value in kwargs.items()])
    return HttpResponse(body, content_type='text/plain')

def list_view(request):
    published = Post.objects.exclude(post_date__exact=None)
    posts = published.order_by('-post_date')
    template = loader.get_template('blogging/list.html')
    context = {'posts': posts}
    body = template.render(context)
    return HttpResponse(body, content_type='text/html')


def detail_view(request, post_id):
    published = Post.objects.exclude(post_date__exact = None)
    try:
        post = published.get(pk=post_id)
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

