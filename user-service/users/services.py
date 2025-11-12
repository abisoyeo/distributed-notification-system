from .models import User, PushToken, NotificationPreferences
from django.db import transaction

class UserService:
    @staticmethod
    def create_user_with_preferences(email, password, name='', push_token=None):
        """Create user with embedded preferences"""
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                push_token=push_token,
                preferences={
                    'email': True,
                    'push': True
                }
            )
            # Optionally create separate NotificationPreferences for backwards compatibility
            NotificationPreferences.objects.create(user=user)
            return user
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user and their push tokens"""
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            PushToken.objects.filter(user=user).update(is_active=False)
            return user
    
    @staticmethod
    def update_preferences(user, email_pref=None, push_pref=None):
        """Update user preferences"""
        if email_pref is not None:
            user.preferences['email'] = email_pref
        if push_pref is not None:
            user.preferences['push'] = push_pref
        user.save()
        return user

class PushTokenService:
    @staticmethod
    def register_token(user, device_id, token, device_type):
        """Register or update push token"""
        push_token, created = PushToken.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'token': token,
                'device_type': device_type,
                'is_active': True
            }
        )
        # Also update user's main push_token field
        user.push_token = token
        user.save()
        return push_token, created