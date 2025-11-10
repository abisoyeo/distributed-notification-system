from django.contrib import admin

# Register your models here.
from .models import User, PushToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'full_name')
    ordering = ('email',)

@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'device_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)