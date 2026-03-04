"""
Blood Stock app admin configuration.
"""

from django.contrib import admin
from .models import BloodStock, StockTransaction


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    """Blood Stock admin."""
    
    list_display = ['blood_group', 'hospital_name', 'units_available', 'units_reserved', 'stock_status', 'last_updated']
    list_filter = ['blood_group', 'hospital_city']
    search_fields = ['hospital_name', 'hospital_city']
    
    def stock_status(self, obj):
        return obj.stock_status.upper()
    stock_status.short_description = 'Status'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    """Stock Transaction admin."""
    
    list_display = ['blood_stock', 'transaction_type', 'units', 'performed_by', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['blood_stock__hospital_name']
    readonly_fields = ['created_at']
