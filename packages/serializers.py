from rest_framework import serializers
from .models import Package, PackageReview, SavedPackage, Departure
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name = 'PackageUserSerializer'

class PackageReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PackageReview
        fields = [
            'id', 'package', 'user', 'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DepartureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departure
        fields = ['id', 'package', 'start_date', 'end_date', 'price', 'available_slots', 'is_guaranteed']
        read_only_fields = ['id']

class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'category', 'location', 'region',
            'price', 'discounted_price', 'duration', 'duration_in_days',
            'image', 'gallery_images', 'rating', 'featured'
        ]
        read_only_fields = ['id', 'slug', 'rating']

class PackageDetailSerializer(PackageListSerializer):
    reviews = PackageReviewSerializer(many=True, read_only=True)
    departures = DepartureSerializer(many=True, read_only=True)
    
    class Meta(PackageListSerializer.Meta):
        fields = PackageListSerializer.Meta.fields + [
            'description', 'short_description', 'included', 'not_included',
            'itinerary', 'departure', 'departure_time', 'return_time',
            'max_group_size', 'min_age', 'difficulty', 'tour_guide',
            'languages', 'coordinates', 'status', 'reviews', 'departures'
        ]
        read_only_fields = PackageListSerializer.Meta.read_only_fields + [
            'status', 'created_at', 'updated_at'
        ]

class PackageSerializer(PackageListSerializer):
    class Meta(PackageListSerializer.Meta):
        fields = PackageListSerializer.Meta.fields + [
            'description', 'short_description', 'included', 'not_included',
            'itinerary', 'departure', 'departure_time', 'return_time',
            'max_group_size', 'min_age', 'difficulty', 'tour_guide',
            'languages', 'coordinates', 'status'
        ]
        read_only_fields = PackageListSerializer.Meta.read_only_fields

    def validate(self, data):
        if 'coordinates' in data and len(data['coordinates']) == 2:
            lat, lon = data['coordinates']
            if not -90 <= lat <= 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90")
            if not -180 <= lon <= 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180")
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavedPackageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    package = PackageListSerializer(read_only=True)
    
    class Meta:
        model = SavedPackage
        fields = ['id', 'user', 'package', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)