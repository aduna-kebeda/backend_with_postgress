from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import BlogPost, BlogComment, SavedPost
from .serializers import (
    BlogPostSerializer, BlogCommentSerializer,
    SavedPostSerializer
)
from django.utils.text import slugify
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="List all blog posts"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Create a new blog post",
        request_body=BlogPostSerializer,
        responses={
            201: BlogPostSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Get a specific blog post",
        responses={
            200: BlogPostSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Update a blog post",
        request_body=BlogPostSerializer,
        responses={
            200: BlogPostSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Partially update a blog post",
        request_body=BlogPostSerializer,
        responses={
            200: BlogPostSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Delete a blog post",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status', None)
        featured_param = self.request.query_params.get('featured', None)
        search_param = self.request.query_params.get('search', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if featured_param:
            featured = featured_param.lower() == 'true'
            queryset = queryset.filter(featured=featured)
        if search_param:
            queryset = queryset.filter(
                Q(title__icontains=search_param) |
                Q(content__icontains=search_param) |
                Q(excerpt__icontains=search_param) |
                Q(tags__contains=[search_param])
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Get featured blog posts",
        responses={
            200: BlogPostSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = self.get_queryset().filter(featured=True, status='published')
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Increment post views",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'views': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        post = self.get_object()
        post.views += 1
        post.save()
        return Response({'views': post.views})

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Toggle featured status",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'featured': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        post = self.get_object()
        post.featured = not post.featured
        post.save()
        return Response({'featured': post.featured})

class BlogCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BlogComment.objects.none()
        post_pk = self.kwargs.get('post_pk')
        if post_pk:
            return BlogComment.objects.filter(post_id=post_pk)
        return BlogComment.objects.none()

    def perform_create(self, serializer):
        post = get_object_or_404(BlogPost, pk=self.kwargs.get('post_pk'))
        serializer.save(post=post, author=self.request.user)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="List comments for a post",
        responses={
            200: BlogCommentSerializer(many=True),
            404: "Post not found"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Create a new comment",
        request_body=BlogCommentSerializer,
        responses={
            201: BlogCommentSerializer,
            400: "Bad Request",
            404: "Post not found"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Get a specific comment",
        responses={
            200: BlogCommentSerializer,
            404: "Comment not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Update a comment",
        request_body=BlogCommentSerializer,
        responses={
            200: BlogCommentSerializer,
            400: "Bad Request",
            404: "Comment not found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Partially update a comment",
        request_body=BlogCommentSerializer,
        responses={
            200: BlogCommentSerializer,
            400: "Bad Request",
            404: "Comment not found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Delete a comment",
        responses={
            204: "No Content",
            404: "Comment not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Mark comment as helpful",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'helpful_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: "Comment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        comment = self.get_object()
        comment.helpful_count += 1
        comment.save()
        return Response({'helpful_count': comment.helpful_count})

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Report a comment",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Comment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        comment = self.get_object()
        comment.reported = True
        comment.save()
        return Response({'message': 'Comment reported successfully'})

class SavedPostViewSet(viewsets.ModelViewSet):
    serializer_class = SavedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="List saved posts"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Save a post",
        request_body=SavedPostSerializer,
        responses={
            201: SavedPostSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog'],
        operation_description="Remove a saved post",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavedPost.objects.none()
        return SavedPost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        post = get_object_or_404(BlogPost, pk=self.kwargs.get('post_pk'))
        if SavedPost.objects.filter(user=self.request.user, post=post).exists():
            raise serializers.ValidationError('Post is already saved')
        serializer.save(user=self.request.user, post=post)