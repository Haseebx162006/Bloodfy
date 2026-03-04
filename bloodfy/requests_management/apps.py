"""
Requests Management app configuration.
"""

from django.apps import AppConfig


class RequestsManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requests_management'
    verbose_name = 'Blood Request Management'
