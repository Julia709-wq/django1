from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'header', 'tag', 'created_at', 'views')
    search_fields = ('header', 'tag')
    list_filter = ('created_at', 'tag')
    ordering = ('-created_at',)

# blogpost_admin
# blog