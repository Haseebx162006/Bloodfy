"""
Bloodfy Project - Django Project Initialization
"""

# Celery is optional for development
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed - running without background tasks
    celery_app = None
    __all__ = ()

