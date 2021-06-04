from django.forms import ModelForm, TextInput, Textarea
from .models import Comment
from django.contrib.auth.forms import UserCreationForm


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
