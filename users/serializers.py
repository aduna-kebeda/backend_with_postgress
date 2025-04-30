from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, BusinessOwnerProfile

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required.')

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name = 'MainUserSerializer'

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 
                 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("New passwords don't match")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_new_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'bio', 'phone', 'date_of_birth', 'gender',
            'country', 'city', 'address',
            'preferred_language', 'preferred_currency',
            'travel_interests', 'accommodation_types',
            'budget_range', 'travel_style',
            'email_notifications', 'push_notifications',
            'sms_notifications', 'marketing_notifications',
            'new_deals_notifications', 'event_reminders',
            'trip_reminders',
            'facebook', 'instagram', 'twitter', 'linkedin',
            'emergency_contact_name', 'emergency_contact_relationship',
            'emergency_contact_phone', 'emergency_contact_email'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessOwnerProfile
        fields = [
            'id', 'business_name', 'business_type', 'business_description',
            'business_phone', 'business_email', 'business_address', 'business_city',
            'business_country', 'business_registration_number', 'business_tax_id',
            'business_license', 'business_logo', 'business_photos',
            'business_social_media', 'business_operating_hours',
            'business_payment_methods', 'business_amenities',
            'business_cancellation_policy', 'business_terms_conditions',
            'business_privacy_policy', 'business_rating', 'business_review_count',
            'is_verified', 'verification_status', 'verification_documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'business_rating', 'business_review_count', 
                          'is_verified', 'verification_status', 'created_at', 'updated_at')

class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'status', 'email_verified')
        read_only_fields = fields

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def validate_new_password(self, value):
        validate_password(value)
        return value

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)