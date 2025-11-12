from .models import User, PushToken, NotificationPreferences
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user
    
class PushTokenSerializer(serializers.ModelSerializer):
    fcm_token = serializers.CharField(source='token', required=True)
    platform = serializers.CharField(source='device_type', required=True)
    
    class Meta:
        model = PushToken
        fields = ['id', 'device_id', 'fcm_token', 'platform', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_active']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferences
        fields = ['email_notifications', 'push_notifications', 'sms_notifications', 'categories']