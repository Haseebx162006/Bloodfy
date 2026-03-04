"""
User management URL routes.
"""

from django.urls import path
from ..views import (
    ProfileView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('', UserListView.as_view(), name='user-list'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
]
