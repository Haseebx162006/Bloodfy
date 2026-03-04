"""
Donors app models.
"""

import uuid
from datetime import date, timedelta
from django.db import models
from django.conf import settings
from utils.constants import BLOOD_GROUPS, DONATION_STATUS, DONATION_ELIGIBILITY_DAYS
from utils.validators import validate_blood_group, validate_latitude, validate_longitude


class Donor(models.Model):
    """
    Donor profile model.
    Contains blood donation-specific information about a user.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donor_profile'
    )
    
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        validators=[validate_blood_group],
        verbose_name='Blood Group'
    )
    
    # Location information
    city = models.CharField(max_length=100)
    
    address = models.TextField(
        blank=True,
        null=True
    )
    
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
    
    # Donation tracking
    last_donation_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Last Donation Date'
    )
    
    donation_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Donations'
    )
    
    # Status fields
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active Donor'
    )
    
    is_eligible = models.BooleanField(
        default=True,
        verbose_name='Is Eligible to Donate'
    )
    
    # Performance metrics
    response_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        verbose_name='Response Rate (%)'
    )
    
    total_requests_received = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Requests Received'
    )
    
    total_requests_accepted = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Requests Accepted'
    )
    
    availability_status = models.BooleanField(
        default=True,
        verbose_name='Currently Available'
    )
    
    # Medical information
    medical_history = models.TextField(
        blank=True,
        null=True,
        verbose_name='Medical History Notes'
    )
    
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Weight (kg)'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    
    # CNIC for Pakistani users
    cnic = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        verbose_name='CNIC'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['city']),
            models.Index(fields=['is_active', 'is_eligible']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"
    
    @property
    def next_eligible_date(self):
        """Calculate the next date when the donor is eligible to donate."""
        if not self.last_donation_date:
            return None
        return self.last_donation_date + timedelta(days=DONATION_ELIGIBILITY_DAYS)
    
    @property
    def days_until_eligible(self):
        """Calculate days remaining until eligible to donate."""
        if not self.last_donation_date:
            return 0
        
        next_date = self.next_eligible_date
        today = date.today()
        
        if today >= next_date:
            return 0
        
        return (next_date - today).days
    
    def update_eligibility(self):
        """Update eligibility status based on last donation date."""
        if not self.last_donation_date:
            self.is_eligible = True
        else:
            today = date.today()
            eligible_date = self.last_donation_date + timedelta(days=DONATION_ELIGIBILITY_DAYS)
            self.is_eligible = today >= eligible_date
        
        self.save(update_fields=['is_eligible'])
        return self.is_eligible
    
    def update_response_rate(self):
        """Update response rate based on request acceptance history."""
        if self.total_requests_received == 0:
            self.response_rate = 100.00
        else:
            self.response_rate = (self.total_requests_accepted / self.total_requests_received) * 100
        
        self.save(update_fields=['response_rate'])
        return self.response_rate
    
    def record_donation(self, donation_date=None):
        """Record a new donation for this donor."""
        self.last_donation_date = donation_date or date.today()
        self.donation_count += 1
        self.is_eligible = False
        self.save(update_fields=['last_donation_date', 'donation_count', 'is_eligible'])


class DonationHistory(models.Model):
    """
    Model to track individual donation records.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name='donation_history'
    )
    
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS
    )
    
    units_donated = models.PositiveIntegerField(
        default=1,
        verbose_name='Units Donated'
    )
    
    donation_date = models.DateField(
        verbose_name='Donation Date'
    )
    
    next_eligible_date = models.DateField(
        verbose_name='Next Eligible Date'
    )
    
    hospital_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=DONATION_STATUS,
        default='completed'
    )
    
    notes = models.TextField(
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Donation History'
        verbose_name_plural = 'Donation Histories'
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.donation_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate next eligible date
        if not self.next_eligible_date:
            self.next_eligible_date = self.donation_date + timedelta(days=DONATION_ELIGIBILITY_DAYS)
        
        # Set blood group from donor if not specified
        if not self.blood_group:
            self.blood_group = self.donor.blood_group
        
        super().save(*args, **kwargs)


class DonorRequest(models.Model):
    """
    Model to store pending donor registration requests.
    Created when a user submits "Become a Donor" form.
    Converted to Donor profile upon admin approval.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donor_request'
    )
    
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        validators=[validate_blood_group],
        verbose_name='Blood Group'
    )
    
    # Location information
    city = models.CharField(max_length=100)
    
    address = models.TextField(
        blank=True,
        null=True
    )
    
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
    
    # Medical information
    medical_history = models.TextField(
        blank=True,
        null=True,
        verbose_name='Medical History Notes'
    )
    
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Weight (kg)'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    
    # CNIC for Pakistani users
    cnic = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='CNIC'
    )
    
    # Request status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        verbose_name='Request Status'
    )
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_donor_requests',
        verbose_name='Reviewed By Admin'
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Reviewed At'
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Rejection Reason'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Donor Request'
        verbose_name_plural = 'Donor Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group} ({self.status})"

