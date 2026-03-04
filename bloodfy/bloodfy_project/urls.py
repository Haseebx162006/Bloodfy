"""
URL configuration for bloodfy_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    """API root endpoint."""
    return JsonResponse({
        'success': True,
        'message': 'Welcome to Bloodfy API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'users': '/api/users/',
            'donors': '/api/donors/',
            'recipients': '/api/recipients/',
            'blood_requests': '/api/blood-requests/',
            'blood_stock': '/api/blood-stock/',
            'ai_engine': '/api/ai/',
            'notifications': '/api/notifications/',
            'chatbot': '/api/chatbot/',
        },
        'documentation': '/api/docs/',
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    
    # Authentication endpoints
    path('api/auth/', include('users.urls.auth_urls')),
    
    # User management endpoints
    path('api/users/', include('users.urls.user_urls')),
    
    # Donor endpoints
    path('api/donors/', include('donors.urls')),
    
    # Recipient endpoints
    path('api/recipients/', include('recipients.urls')),
    
    # Blood request endpoints
    path('api/blood-requests/', include('requests_management.urls')),
    
    # Blood stock endpoints
    path('api/blood-stock/', include('blood_stock.urls')),
    
    # AI engine endpoints
    path('api/ai/', include('ai_engine.urls')),
    
    # Notification endpoints
    path('api/notifications/', include('notifications.urls')),
    
    # Chatbot endpoints
    path('api/chatbot/', include('chatbot.urls')),
]
