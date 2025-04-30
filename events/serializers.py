from rest_framework import serializers
from .models import Event, EventReview, EventRegistration, SavedEvent, EventSubscription
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name = 'EventUserSerializer'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'title', 'slug', 'description', 'category',
            'location', 'address', 'latitude', 'longitude', 'start_date', 'end_date', 
            'images', 'capacity', 'current_attendees', 'price', 'featured', 
            'status', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'slug', 'current_attendees',
                           'rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)

class EventListSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        fields = [
            'id', 'title', 'slug', 'category', 'location', 'start_date',
            'end_date', 'images', 'featured', 'status', 'current_attendees', 'rating'
        ]
        read_only_fields = ['id', 'slug', 'status', 'current_attendees', 'rating']

class EventDetailSerializer(EventSerializer):
    reviews = serializers.SerializerMethodField()
    registrations = serializers.SerializerMethodField()
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['reviews', 'registrations']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all().order_by('-created_at')[:5]
        return EventReviewSerializer(reviews, many=True).data
    
    def get_registrations(self, obj):
        registrations = obj.registrations.filter(status='confirmed')
        return EventRegistrationSerializer(registrations, many=True).data

class EventReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventReview
        fields = [
            'id', 'event', 'user', 'rating', 'title', 'content',
            'helpful', 'reported', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'helpful', 'reported', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavedEventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventListSerializer(read_only=True)
    
    class Meta:
        model = SavedEvent
        fields = ['id', 'user', 'event', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class EventSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSubscription
        fields = ['id', 'email', 'categories', 'created_at']
        read_only_fields = ['id', 'created_at']