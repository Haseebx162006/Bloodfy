"""
Recipients app admin configuration.
"""

from django.contrib import admin
from .models import Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Recipient admin."""
    
    list_display = ['get_name', 'hospital_name', 'hospital_city', 'is_active']
    list_filter = ['hospital_city', 'is_active']
    search_fields = ['user__email', 'hospital_name', 'patient_name']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
