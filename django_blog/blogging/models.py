from django.db import models
from django.db.models.deletion import CASCADE

class Post(models.Model):
    title = models.CharField(max_length=128)
    text = models.CharField(blank=True)
    author = models.ForeignKey(User, on_delete=CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    post_date = models.DateField(blank=True, null=True)
