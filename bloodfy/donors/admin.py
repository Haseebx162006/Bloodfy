"""
Donors app admin configuration.
"""

from django.contrib import admin
from .models import Donor, DonationHistory


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """Donor admin."""
    
    list_display = ['get_name', 'blood_group', 'city', 'is_active', 'is_eligible', 'donation_count']
    list_filter = ['blood_group', 'is_active', 'is_eligible', 'city']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'cnic']
    readonly_fields = ['donation_count', 'response_rate', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    """Donation History admin."""
    
    list_display = ['get_donor_name', 'blood_group', 'units_donated', 'donation_date', 'status']
    list_filter = ['blood_group', 'status', 'donation_date']
    search_fields = ['donor__user__email', 'hospital_name']
    
    def get_donor_name(self, obj):
        return obj.donor.user.get_full_name()
    get_donor_name.short_description = 'Donor'
