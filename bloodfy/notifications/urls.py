"""
Notifications app URL routes.
"""

from django.urls import path
from .views import (
    NotificationListView,
    SendManualNotificationView,
    NotificationLogsView,
    NotificationStatsView,
    NotificationTemplateListView,
    AppNotificationAPIView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('send-manual/', SendManualNotificationView.as_view(), name='notification-send'),
    path('logs/', NotificationLogsView.as_view(), name='notification-logs'),
    path('stats/', NotificationStatsView.as_view(), name='notification-stats'),
    path('templates/', NotificationTemplateListView.as_view(), name='notification-templates'),
    path('app/', AppNotificationAPIView.as_view(), name='app-notification-list'),
    path('app/<uuid:notification_id>/', AppNotificationAPIView.as_view(), name='app-notification-detail'),
]
