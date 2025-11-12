import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='')  # Changed from full_name to name, added default
    email = models.EmailField(unique=True)
    push_token = models.CharField(max_length=512, blank=True, null=True)  # Added push_token
    # password is inherited from AbstractBaseUser (hashed automatically)
    preferences = models.JSONField(default=dict, blank=True)  # Added preferences as JSONField
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Changed from date_joined
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  # Added updated_at

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Changed from full_name
    
    def save(self, *args, **kwargs):
        # Set default preferences if not provided
        if not self.preferences:
            self.preferences = {
                'email': True,
                'push': True
            }
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email


class PushToken(models.Model):
    ANDROID = 'android'
    IOS = 'ios'
    WEB = 'web'
    OTHER = 'other'

    DEVICE_CHOICES = [
        (ANDROID, 'Android'),
        (IOS, 'iOS'),
        (WEB, 'Web'),
        (OTHER, 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='push_tokens')
    device_id = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=512)
    device_type = models.CharField(max_length=32, choices=DEVICE_CHOICES, default=OTHER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Push Token'
        verbose_name_plural = 'Push Tokens'
        unique_together = ('user', 'token')

    def __str__(self):
        return f"{self.user.email} - {self.device_type}"


class NotificationPreferences(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    categories = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"