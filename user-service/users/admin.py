from django.contrib import admin
from .models import User, PushToken, NotificationPreferences

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_staff', 'created_at', 'updated_at')
    search_fields = ('email', 'name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'device_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications', 'sms_notifications', 'categories')
    search_fields = ('user__email',)
    ordering = ('user__email',)
    readonly_fields = ('id',)