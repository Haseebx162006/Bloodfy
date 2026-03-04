"""
Recipients app configuration.
"""

from django.apps import AppConfig


class RecipientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipients'
    verbose_name = 'Recipient Management'
