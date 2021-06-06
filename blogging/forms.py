from django.db.models.base import Model
from django.forms import ModelForm, TextInput, Textarea, DateInput
from .models import Comment, Post
from django.contrib.auth.forms import UserCreationForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "author", "post_date"]
        widgets = {
            "title": TextInput(),
            "text": Textarea(),
            "author": TextInput({"hidden": True, "readonly": True}),
            "post_date": DateInput(attrs={"class": "datepicker"}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["author", "post", "text"]
        widgets = {
            "author": TextInput({"readonly": True, "hidden": True}),
            "post": TextInput({"readonly": True, "hidden": True}),
            "text": Textarea(),
        }
        labels = {"text": ("New comment: "), "author": (""), "post": ("")}


class NewUserForm(UserCreationForm):
    """from https://realpython.com/django-user-management/#register-new-users"""

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
        labels = {"email": ("Email address(optional) ")}
