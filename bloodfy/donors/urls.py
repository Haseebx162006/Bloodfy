"""
Donors app URL routes.
"""

from django.urls import path
from .views import (
    DonorListView,
    DonorRegisterView,
    DonorDetailView,
    DonorEligibilityView,
    DonationHistoryView,
    DonorStatisticsView,
    DonorReactivateView,
    DonorPendingListView,
    DonorApprovalView,
    AdminDonorCreateView,
)
from .emergency_views import (
    EmergencyDonorSearchView,
    EmergencyContactView,
)

urlpatterns = [
    path('', DonorListView.as_view(), name='donor-list'),
    path('register/', DonorRegisterView.as_view(), name='donor-register'),
    path('create/', AdminDonorCreateView.as_view(), name='donor-create-admin'),
    path('eligibility-status/', DonorEligibilityView.as_view(), name='donor-eligibility'),
    path('statistics/', DonorStatisticsView.as_view(), name='donor-statistics'),
    
    # Emergency endpoints
    path('emergency/search/', EmergencyDonorSearchView.as_view(), name='emergency-donor-search'),
    path('emergency/contact/', EmergencyContactView.as_view(), name='emergency-contact'),
    
    # Admin endpoints for donor approval
    path('pending/', DonorPendingListView.as_view(), name='donor-pending-list'),
    path('requests/<uuid:request_id>/approve/', DonorApprovalView.as_view(), name='donor-approval'),
    
    path('<uuid:donor_id>/', DonorDetailView.as_view(), name='donor-detail'),
    path('<uuid:donor_id>/donation-history/', DonationHistoryView.as_view(), name='donor-history'),
    path('<uuid:donor_id>/reactivate/', DonorReactivateView.as_view(), name='donor-reactivate'),
]
