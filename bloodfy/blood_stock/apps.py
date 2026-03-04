"""
Blood Stock app configuration.
"""

from django.apps import AppConfig


class BloodStockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blood_stock'
    verbose_name = 'Blood Stock Management'
