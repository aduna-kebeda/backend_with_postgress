from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
import uuid

User = get_user_model()

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    tags = models.JSONField(default=list)
    imageUrl = models.URLField(max_length=500, blank=True, default="https://example.com/default-image.jpg")
    
    # Author Information
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='blog_posts', null=True)
    authorName = models.CharField(max_length=200, blank=True)
    authorImage = models.URLField(max_length=500, blank=True, null=True)
    
    # Status and Statistics
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    views = models.PositiveIntegerField(default=0)
    readTime = models.PositiveIntegerField(default=5)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.authorName and self.author:
            self.authorName = self.author.get_full_name() or self.author.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='blog_comments', null=True)
    content = models.TextField()
    helpful = models.PositiveIntegerField(default=0)
    reported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Comment'
        verbose_name_plural = 'Blog Comments'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

class SavedPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        related_name='saved_posts',
        null=True
    )
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        verbose_name = 'Saved Post'
        verbose_name_plural = 'Saved Posts'

    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"