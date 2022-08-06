from django.contrib import admin
from .models import Category, Post, Comment, EarlyAccess


admin.site.register(Category)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "overview","timestamp")
    list_filter = ("timestamp","status")
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "body", "post", "created_on", "active")
    list_filter = ("active", "created_on")
    search_fields = ("name", "email", "body")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


# MAX_OBJECTS = 1

# @admin.register(EarlyAccess)
# class EarlyAccessAdmin(admin.ModelAdmin):
#     list_display = ("heading","description")
#     def has_add_permission(self, request):
#         if self.model.objects.count() >= MAX_OBJECTS:
#             return False
#         return super().has_add_permission(request)
#     def has_delete_permission(self, request, obj=None):
#         return False
