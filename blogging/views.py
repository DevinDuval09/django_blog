from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Post
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CommentForm, NewUserForm
from django.contrib.auth import login


def stub_view(request, *args, **kwargs):
    body = "Stub View\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join([f"\t{arg}" for arg in args])
    if kwargs:
        body += "Kwargs:\n"
        body += "\n".join([f"\t{tup}" for tup in kwargs.items()])
    return HttpResponse(body, content_type="text/plain")


def add_comment(request, *args, **kwargs):
    form = CommentForm(request.POST)
    if form.is_valid():
        model_instance = form.save(commit=False)
        model_instance.save()
        return redirect(f"/posts/{kwargs['pk']}/comments")
    else:
        form = CommentForm(initial={"post": kwargs["pk"], "author": request.user})
        return render(
            request,
            "blogging/comment.html",
            {"form": form, "post": Post.objects.get(pk=kwargs["pk"])},
        )


def create_user(request, *args, **kwargs):
    form = NewUserForm(request.POST)
    redirect_page = request.POST.get("detail", "/")
    if form.is_valid():
        user = form.save(commit=False)
        user.save()
        login(request, user)
        return HttpResponseRedirect(redirect_to=redirect_page)
    else:
        return render(request, "new_user.html", {"form": form})


class PostListAllView(ListView):
    model = Post
    template_name = "blogging/list.html"


class PostPostedList(ListView):
    queryset = Post.objects.exclude(post_date=None).order_by("-post_date")
    template_name = "blogging/list.html"


class PostDetail(DetailView):
    queryset = Post.objects.exclude(post_date=None)
    template_name = "blogging/detail.html"

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context["form"] = CommentForm(
            initial={"post": kwargs["object"].pk, "user": self.request.user.pk}
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.user.id is None:
            return redirect("/login/")

        form = CommentForm(
            {
                "post": request.POST.get("post"),
                "author": request.user.id,
                "text": request.POST.get("text"),
            }
        )
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.save()
            return redirect(f'/posts/{kwargs["pk"]}')
        else:
            return stub_view(form_errors=form.errors)


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
