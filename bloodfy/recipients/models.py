"""
Recipients app models.
"""

import uuid
from django.db import models
from django.conf import settings
from utils.validators import validate_latitude, validate_longitude, validate_phone_number


class Recipient(models.Model):
    """
    Recipient profile model.
    Contains hospital/patient information for blood request handling.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipient_profile'
    )
    
    # Hospital information
    hospital_name = models.CharField(
        max_length=255,
        verbose_name='Hospital Name'
    )
    
    hospital_address = models.TextField(
        verbose_name='Hospital Address'
    )
    
    hospital_city = models.CharField(
        max_length=100,
        verbose_name='City'
    )
    
    # Location coordinates
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[validate_latitude]
    )
    
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[validate_longitude]
    )
    
    # Contact information
    emergency_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        verbose_name='Emergency Contact'
    )
    
    secondary_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        verbose_name='Secondary Contact'
    )
    
    # Patient information (optional)
    patient_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Patient Name'
    )
    
    patient_age = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Patient Age'
    )
    
    doctor_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Doctor Name'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Hospital Department'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hospital_city']),
            models.Index(fields=['hospital_name']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hospital_name}"
