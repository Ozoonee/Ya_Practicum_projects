from django.contrib import admin
from . import models
from .models import Comment

admin.site.register(models.Category)
admin.site.register(models.Location)
admin.site.register(models.Post)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'text', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['text']
    raw_id_fields = ['post']
