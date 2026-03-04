"""
Recipients app URL routes.
"""

from django.urls import path
from .views import (
    RecipientRegisterView,
    RecipientProfileView,
    RecipientListView,
    RecipientDetailView,
)

urlpatterns = [
    path('register/', RecipientRegisterView.as_view(), name='recipient-register'),
    path('profile/', RecipientProfileView.as_view(), name='recipient-profile'),
    path('', RecipientListView.as_view(), name='recipient-list'),
    path('<uuid:recipient_id>/', RecipientDetailView.as_view(), name='recipient-detail'),
]
