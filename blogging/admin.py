from django.contrib import admin
from .models import Category, Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment


class CategoryInline(admin.TabularInline):
    model = Category.posts.through


class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "text", "post_date"]
    inlines = [CategoryInline, CommentInline]
    ordering = ["title"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "text", "created_time"]
    ordering = ["-created_time"]
    exclude = ["post"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    ordering = ["name"]
    exclude = ["posts"]
    # actions = [list_categories]


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
