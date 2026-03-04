"""
Blood Stock app models.
"""

import uuid
from django.db import models
from django.utils import timezone
from utils.constants import BLOOD_GROUPS
from utils.validators import validate_blood_group


class BloodStock(models.Model):
    """
    Blood Stock inventory model.
    Tracks blood units available at hospitals/blood banks.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        validators=[validate_blood_group],
        verbose_name='Blood Group'
    )
    
    # Stock quantities
    units_available = models.PositiveIntegerField(
        default=0,
        verbose_name='Units Available'
    )
    
    units_reserved = models.PositiveIntegerField(
        default=0,
        verbose_name='Units Reserved'
    )
    
    units_expired = models.PositiveIntegerField(
        default=0,
        verbose_name='Units Expired (Total)'
    )
    
    # Hospital/Blood Bank information
    hospital_name = models.CharField(
        max_length=255,
        verbose_name='Hospital/Blood Bank Name'
    )
    
    hospital_address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Address'
    )
    
    hospital_city = models.CharField(
        max_length=100,
        verbose_name='City'
    )
    
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Contact Number'
    )
    
    # Thresholds for alerts
    minimum_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name='Minimum Stock Threshold'
    )
    
    critical_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name='Critical Stock Threshold'
    )
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blood Stock'
        verbose_name_plural = 'Blood Stocks'
        unique_together = ['blood_group', 'hospital_name']
        ordering = ['hospital_name', 'blood_group']
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['hospital_city']),
            models.Index(fields=['units_available']),
        ]
    
    def __str__(self):
        return f"{self.hospital_name} - {self.blood_group}: {self.units_available} units"
    
    @property
    def total_units(self):
        """Total units including reserved."""
        return self.units_available + self.units_reserved
    
    @property
    def actual_available(self):
        """Units actually available (excluding reserved)."""
        return self.units_available
    
    @property
    def is_low(self):
        """Check if stock is below minimum threshold."""
        return self.units_available <= self.minimum_threshold
    
    @property
    def is_critical(self):
        """Check if stock is at critical level."""
        return self.units_available <= self.critical_threshold
    
    @property
    def stock_status(self):
        """Get stock status string."""
        if self.is_critical:
            return 'critical'
        elif self.is_low:
            return 'low'
        return 'normal'
    
    def reserve_units(self, units):
        """Reserve units for a blood request."""
        if units > self.units_available:
            raise ValueError("Not enough units available to reserve")
        
        self.units_available -= units
        self.units_reserved += units
        self.save(update_fields=['units_available', 'units_reserved', 'last_updated'])
    
    def release_reserved(self, units):
        """Release reserved units back to available."""
        if units > self.units_reserved:
            units = self.units_reserved
        
        self.units_reserved -= units
        self.units_available += units
        self.save(update_fields=['units_available', 'units_reserved', 'last_updated'])
    
    def fulfill_reserved(self, units):
        """Fulfill reserved units (remove from inventory)."""
        if units > self.units_reserved:
            units = self.units_reserved
        
        self.units_reserved -= units
        self.save(update_fields=['units_reserved', 'last_updated'])
    
    def add_units(self, units):
        """Add new units to stock."""
        self.units_available += units
        self.save(update_fields=['units_available', 'last_updated'])
    
    def expire_units(self, units):
        """Mark units as expired."""
        if units > self.units_available:
            units = self.units_available
        
        self.units_available -= units
        self.units_expired += units
        self.save(update_fields=['units_available', 'units_expired', 'last_updated'])


class StockTransaction(models.Model):
    """
    Track all stock transactions for audit purposes.
    """
    
    TRANSACTION_TYPES = [
        ('addition', 'Stock Addition'),
        ('reservation', 'Reservation'),
        ('release', 'Release from Reservation'),
        ('fulfillment', 'Fulfillment'),
        ('expiry', 'Expiry'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    blood_stock = models.ForeignKey(
        BloodStock,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    
    units = models.IntegerField(
        verbose_name='Units Changed'
    )
    
    units_before = models.PositiveIntegerField(
        verbose_name='Units Before'
    )
    
    units_after = models.PositiveIntegerField(
        verbose_name='Units After'
    )
    
    blood_request = models.ForeignKey(
        'requests_management.BloodRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_transactions'
    )
    
    performed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_transactions'
    )
    
    notes = models.TextField(
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.blood_stock} - {self.transaction_type}: {self.units} units"
