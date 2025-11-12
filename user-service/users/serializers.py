from .models import User, PushToken, NotificationPreferences
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'push_token', 'password', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set default preferences if not provided
        if 'preferences' not in validated_data:
            validated_data['preferences'] = {
                'email': True,
                'push': True
            }
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            push_token=validated_data.get('push_token'),
            preferences=validated_data.get('preferences')
        )
        return user
    
    def update(self, instance, validated_data):
        # Don't allow password updates through this serializer
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

    
class PushTokenSerializer(serializers.ModelSerializer):
    # ✅ Use snake_case consistently
    device_id = serializers.CharField(required=False, allow_blank=True)
    token = serializers.CharField(required=True)  # Changed from fcm_token
    device_type = serializers.CharField(required=True)  # Changed from platform
    
    class Meta:
        model = PushToken
        fields = ['id', 'device_id', 'token', 'device_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_active']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    # ✅ All snake_case
    email_notifications = serializers.BooleanField(default=True)
    push_notifications = serializers.BooleanField(default=True)
    sms_notifications = serializers.BooleanField(default=False)
    
    class Meta:
        model = NotificationPreferences
        fields = ['email_notifications', 'push_notifications', 'sms_notifications', 'categories']