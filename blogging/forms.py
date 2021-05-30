from logging import disable
from django.forms import ModelForm, TextInput
from .models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["author", "post", "text"]
        widgets = {
            "author": TextInput({"readonly": True, "hidden": True}),
            "post": TextInput({"readonly": True, "hidden": True}),
        }
        labels = {"text": ("New comment: "), "author": (""), "post": ("")}
