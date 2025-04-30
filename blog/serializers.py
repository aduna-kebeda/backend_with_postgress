from rest_framework import serializers
from .models import BlogPost, BlogComment, SavedPost
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    ref_name = 'BlogUserSerializer'
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields

class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    authorName = serializers.CharField(source='author.get_full_name', read_only=True)
    authorImage = serializers.URLField(source='author.profile.avatar', read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'tags',
            'imageUrl', 'author', 'authorName', 'authorImage', 'status',
            'views', 'readTime', 'featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'created_at', 'updated_at']
        extra_kwargs = {
            'status': {'default': 'draft'},
            'featured': {'default': False},
            'readTime': {'required': False, 'default': 5}
        }

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data)

class BlogCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = BlogComment
        fields = [
            'id', 'post', 'author', 'content', 'helpful_count',
            'reported', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'helpful_count', 'reported',
                           'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class SavedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = BlogPostSerializer(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'saved_at']
        read_only_fields = ['id', 'user', 'saved_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)