"""
Celery configuration for bloodfy_project project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodfy_project.settings')

app = Celery('bloodfy_project')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    # Check and reactivate eligible donors every day at 6 AM
    'reactivate-eligible-donors': {
        'task': 'donors.tasks.reactivate_eligible_donors_task',
        'schedule': crontab(hour=6, minute=0),
    },
    # Check for expired blood stock every day at midnight
    'check-expired-blood-stock': {
        'task': 'blood_stock.tasks.check_expired_stock_task',
        'schedule': crontab(hour=0, minute=0),
    },
    # Send reminder notifications for pending requests every hour
    'send-pending-request-reminders': {
        'task': 'notifications.tasks.send_pending_request_reminders_task',
        'schedule': crontab(minute=0),  # Every hour
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
