from rest_framework import serializers
from .models import Business, BusinessReview, SavedBusiness
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name = 'BusinessUserSerializer'

class BusinessReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = BusinessReview
        fields = [
            'id', 'business', 'user', 'rating', 'comment',
            'helpful_votes', 'is_reported', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'helpful_votes', 'is_reported', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BusinessReviewCreateSerializer(BusinessReviewSerializer):
    class Meta(BusinessReviewSerializer.Meta):
        fields = ['rating', 'comment']

class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'slug', 'business_type', 'description',
            'contact_email', 'contact_phone', 'website', 'region', 'city',
            'address', 'latitude', 'longitude', 'main_image', 'gallery_images',
            'social_media_links', 'opening_hours', 'facilities', 'services',
            'team', 'status', 'is_verified', 'is_featured', 'verification_date',
            'average_rating', 'total_reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'status', 'is_verified', 'is_featured',
                           'verification_date', 'average_rating', 'total_reviews',
                           'created_at', 'updated_at']

class BusinessDetailSerializer(BusinessListSerializer):
    reviews = BusinessReviewSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta(BusinessListSerializer.Meta):
        fields = BusinessListSerializer.Meta.fields + ['owner', 'reviews']

class BusinessCreateSerializer(BusinessListSerializer):
    class Meta(BusinessListSerializer.Meta):
        fields = [
            'name', 'business_type', 'description', 'contact_email',
            'contact_phone', 'website', 'region', 'city', 'address',
            'latitude', 'longitude', 'main_image', 'gallery_images',
            'social_media_links', 'opening_hours', 'facilities',
            'services', 'team'
        ]

class SavedBusinessSerializer(serializers.ModelSerializer):
    business = BusinessListSerializer(read_only=True)
    
    class Meta:
        model = SavedBusiness
        fields = ['id', 'user', 'business', 'saved_at']
        read_only_fields = ['id', 'user', 'saved_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)