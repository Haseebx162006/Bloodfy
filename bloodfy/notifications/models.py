"""
Notifications app models.
"""

import uuid
from django.db import models
from django.conf import settings
from donors.models import Donor
from requests_management.models import BloodRequest
from utils.constants import NOTIFICATION_TYPES, DELIVERY_STATUS, RESPONSE_STATUS


class NotificationLog(models.Model):
    """
    Log all notifications sent to donors.
    Tracks delivery status and responses.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name='notifications',
        blank=True,
        null=True
    )
    
    # Notification details
    message_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='sms',
        verbose_name='Message Type'
    )
    
    message_content = models.TextField(
        verbose_name='Message Content'
    )
    
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Subject (for email)'
    )
    
    # Recipient info
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    recipient_email = models.EmailField(
        blank=True,
        null=True
    )
    
    # Delivery tracking
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS,
        default='pending',
        verbose_name='Delivery Status'
    )
    
    delivery_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Delivery Error Message'
    )
    
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Retry Count'
    )
    
    max_retries = models.PositiveIntegerField(
        default=3,
        verbose_name='Maximum Retries'
    )
    
    # External service tracking
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='External Message ID (Twilio SID etc.)'
    )
    
    # Response tracking
    response_status = models.CharField(
        max_length=20,
        choices=RESPONSE_STATUS,
        default='pending',
        verbose_name='Donor Response'
    )
    
    response_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Response Timestamp'
    )
    
    # Timestamps
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Sent Timestamp'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['delivery_status']),
            models.Index(fields=['blood_request']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.message_type.upper()} to {self.donor} - {self.delivery_status}"
    
    def can_retry(self):
        """Check if notification can be retried."""
        return self.retry_count < self.max_retries and self.delivery_status == 'failed'


class NotificationTemplate(models.Model):
    """
    Templates for notification messages.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Template Name'
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='sms'
    )
    
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Email Subject Template'
    )
    
    content = models.TextField(
        verbose_name='Message Template',
        help_text='Use {variable_name} for dynamic content'
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.message_type})"
    
    def render(self, context):
        """Render template with context variables."""
        content = self.content
        subject = self.subject
        
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
            if subject:
                subject = subject.replace(f'{{{key}}}', str(value))
        
        return {
            'subject': subject,
            'content': content
        }

class AppNotification(models.Model):
    """
    In-app notifications for users and admins.
    Used for dashboard notification panels.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='app_notifications'
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Type of notification for icon/color display
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('info', 'Information'),
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('danger', 'Danger'),
            ('blood_request', 'Blood Request'),
            ('donor_approval', 'Donor Approval'),
        ],
        default='info'
    )
    
    # Link to related objects (optional)
    related_id = models.CharField(max_length=255, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'App Notification'
        verbose_name_plural = 'App Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
