from django.contrib import admin
from .models import BlogPost, BlogComment, SavedPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'views', 'featured')
    list_filter = ('status', 'featured', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'helpful_count', 'reported', 'created_at')
    list_filter = ('reported', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')

@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'post__title')
    readonly_fields = ('saved_at',) 