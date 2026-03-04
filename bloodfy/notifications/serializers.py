"""
Notifications app serializers.
"""

from rest_framework import serializers
from .models import NotificationLog, NotificationTemplate, AppNotification


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification log details."""
    
    donor_name = serializers.SerializerMethodField()
    donor_phone = serializers.CharField(source='donor.user.phone_number', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'donor', 'donor_name', 'donor_phone',
            'blood_request', 'message_type', 'message_content',
            'subject', 'recipient_phone', 'recipient_email',
            'delivery_status', 'delivery_error', 'retry_count',
            'external_id', 'response_status', 'response_at',
            'sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'external_id', 'sent_at', 'created_at', 'updated_at'
        ]
    
    def get_donor_name(self, obj):
        return obj.donor.user.get_full_name()


class NotificationLogListSerializer(serializers.ModelSerializer):
    """Serializer for listing notification logs (compact view)."""
    
    donor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'donor_name', 'message_type',
            'delivery_status', 'response_status',
            'sent_at', 'created_at'
        ]
    
    def get_donor_name(self, obj):
        return obj.donor.user.get_full_name()


class SendManualNotificationSerializer(serializers.Serializer):
    """Serializer for sending manual notification."""
    
    donor_id = serializers.UUIDField()
    message_type = serializers.ChoiceField(
        choices=['sms', 'email'],
        default='sms'
    )
    message_content = serializers.CharField()
    subject = serializers.CharField(required=False, allow_blank=True)
    blood_request_id = serializers.UUIDField(required=False, allow_null=True)


class SendBulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications."""
    
    donor_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    message_type = serializers.ChoiceField(
        choices=['sms', 'email'],
        default='sms'
    )
    template_id = serializers.UUIDField(required=False)
    message_content = serializers.CharField(required=False)
    subject = serializers.CharField(required=False, allow_blank=True)
    blood_request_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate(self, attrs):
        if not attrs.get('template_id') and not attrs.get('message_content'):
            raise serializers.ValidationError(
                "Either template_id or message_content must be provided."
            )
        return attrs


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'message_type', 'subject', 'content',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    delivery_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    response_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    by_type = serializers.DictField()
    by_status = serializers.DictField()

class AppNotificationSerializer(serializers.ModelSerializer):
    """Serializer for in-app notifications."""
    
    class Meta:
        model = AppNotification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'related_id', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
