from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=128)
    text = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    post_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    posts = models.ManyToManyField(Post, related_name='categories', blank=True)

    def __str__(self):
        return self.name
    
    def post_titles(self):
        return [post.title for post in self.posts.all()]
