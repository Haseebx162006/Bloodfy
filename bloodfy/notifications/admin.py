"""
Notifications app admin configuration.
"""

from django.contrib import admin
from .models import NotificationLog, NotificationTemplate


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Notification Log admin."""
    
    list_display = ['donor', 'message_type', 'delivery_status', 'response_status', 'sent_at']
    list_filter = ['message_type', 'delivery_status', 'response_status']
    search_fields = ['donor__user__email', 'recipient_phone']
    readonly_fields = ['created_at', 'sent_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Notification Template admin."""
    
    list_display = ['name', 'message_type', 'is_active', 'created_at']
    list_filter = ['message_type', 'is_active']
    search_fields = ['name']
