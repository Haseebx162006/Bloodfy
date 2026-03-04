"""
Requests Management app URL routes.
"""

from django.urls import path
from .views import (
    BloodRequestListView,
    BloodRequestDetailView,
    BloodRequestApproveView,
    BloodRequestCompleteView,
    BloodRequestAssignView,
    MatchedDonorsView,
    EmergencySearchView,
    DonorResponseView,
)

urlpatterns = [
    path('', BloodRequestListView.as_view(), name='blood-request-list'),
    path('emergency-search/', EmergencySearchView.as_view(), name='emergency-search'),
    path('responses/', DonorResponseView.as_view(), name='donor-responses'),
    path('responses/<uuid:response_id>/', DonorResponseView.as_view(), name='donor-response-detail'),
    path('<uuid:request_id>/', BloodRequestDetailView.as_view(), name='blood-request-detail'),
    path('<uuid:request_id>/approve/', BloodRequestApproveView.as_view(), name='blood-request-approve'),
    path('<uuid:request_id>/assign/', BloodRequestAssignView.as_view(), name='blood-request-assign'),
    path('<uuid:request_id>/complete/', BloodRequestCompleteView.as_view(), name='blood-request-complete'),
    path('<uuid:request_id>/matched-donors/', MatchedDonorsView.as_view(), name='blood-request-matched-donors'),
]
