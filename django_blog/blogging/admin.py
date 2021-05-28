from django.contrib import admin
from .models import Category, Post


class CategoryInline(admin.TabularInline):
    model = Category.posts.through


class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "text", "post_date"]
    inlines = [CategoryInline]
    ordering = ["title"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    ordering = ["name"]
    exclude = ["posts"]
    # actions = [list_categories]


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
