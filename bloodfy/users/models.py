"""
Users app models.
"""

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from utils.constants import USER_TYPES, DONOR_STATUS
from utils.validators import validate_phone_number


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for Bloodfy application.
    Uses email as the primary identifier instead of username.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Override username to make it optional
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='Email Address'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        verbose_name='Phone Number'
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='user',
        verbose_name='User Type'
    )
    
    # Donor Status (separate from user_type)
    donor_status = models.CharField(
        max_length=20,
        choices=DONOR_STATUS,
        blank=True,
        null=True,
        verbose_name='Donor Status'
    )
    
    donor_status_updated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Donor Status Updated At'
    )
    
    donor_status_updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='donor_status_updates',
        verbose_name='Donor Status Updated By'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verified'
    )
    
    # Profile fields
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    address = models.TextField(
        blank=True,
        null=True
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['donor_status']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """Return the first name of the user."""
        return self.first_name or self.email.split('@')[0]


class OTPVerification(models.Model):
    """Model for storing OTP codes for email verification."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_codes'
    )
    
    code = models.CharField(max_length=6)
    
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('email_verification', 'Email Verification'),
            ('password_reset', 'Password Reset'),
        ],
        default='email_verification'
    )
    
    is_used = models.BooleanField(default=False)
    
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.purpose}"
    
    @property
    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the OTP is still valid."""
        return not self.is_used and not self.is_expired
