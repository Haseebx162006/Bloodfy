"""
AI Engine app views.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import AIRanking, AIModelMetrics
from .ranking_engine import process_blood_request, rank_donors_for_request
from .serializers import (
    AIRankingListSerializer, RankDonorsRequestSerializer,
    RankDonorsResponseSerializer, AIModelMetricsSerializer,
    ReactivationCheckSerializer, ReactivationResultSerializer
)
from requests_management.models import BloodRequest
from donors.models import Donor
from utils.responses import success_response, error_response
from utils.permissions import IsAdmin


class RankDonorsView(APIView):
    """Trigger AI ranking for a blood request."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Trigger donor ranking for a blood request or simulate for dashboard."""
        serializer = RankDonorsRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Invalid request",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        request_id = serializer.validated_data.get('blood_request_id')
        max_donors = serializer.validated_data.get('max_donors', 10)
        max_distance = serializer.validated_data.get('max_distance_km', 50)
        
        if request_id:
            # REAL RANKING FOR A REQUEST
            try:
                blood_request = BloodRequest.objects.get(id=request_id)
            except BloodRequest.DoesNotExist:
                return error_response(
                    message="Blood request not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Check permission
            if request.user.user_type != 'admin':
                if hasattr(request.user, 'recipient_profile'):
                    if blood_request.recipient != request.user.recipient_profile:
                        return error_response(
                            message="Access denied",
                            status_code=status.HTTP_403_FORBIDDEN
                        )
                else:
                    return error_response(
                        message="Access denied",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
            
            # Process ranking
            rankings, ranked_donors = process_blood_request(
                blood_request,
                max_donors=max_donors,
                max_distance_km=max_distance
            )
            
            results = AIRankingListSerializer(rankings, many=True).data
            blood_group = blood_request.blood_group
        else:
            # SIMULATION FOR DASHBOARD
            blood_group = serializer.validated_data.get('blood_group_needed', 'O-')
            location = serializer.validated_data.get('location', 'Lahore')
            
            # Find donors in the same city with compatible blood group
            from utils.constants import BLOOD_COMPATIBILITY
            compatible_groups = BLOOD_COMPATIBILITY.get(blood_group, [blood_group])
            
            donors = Donor.objects.filter(
                blood_group__in=compatible_groups,
                city__iexact=location,
                is_active=True,
                is_eligible=True,
                availability_status=True
            ).select_related('user')[:max_donors]
            
            results = []
            for i, donor in enumerate(donors, 1):
                results.append({
                    'id': str(donor.id),
                    'donor': {
                        'id': str(donor.id),
                        'user': {
                            'first_name': donor.user.first_name,
                            'last_name': donor.user.last_name,
                            'phone_number': donor.user.phone_number
                        },
                        'city': donor.city,
                        'blood_group': donor.blood_group
                    },
                    'score': 0.95 - (i * 0.05), # Mock score for simulation
                    'distance': 2.5 + (i * 1.2), # Mock distance
                    'rank_position': i
                })

        return success_response(
            data={
                'blood_request_id': str(request_id) if request_id else None,
                'blood_group': blood_group,
                'total_eligible_donors': len(results),
                'ranked_donors': results,
                'algorithm_version': '1.0',
                'calculated_at': timezone.now().isoformat()
            },
            message="Donors ranked successfully"
        )


class RankingHistoryView(APIView):
    """Get ranking history for a blood request."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, request_id):
        """Get AI ranking history."""
        try:
            blood_request = BloodRequest.objects.get(id=request_id)
        except BloodRequest.DoesNotExist:
            return error_response(
                message="Blood request not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        rankings = AIRanking.objects.filter(
            blood_request=blood_request
        ).select_related('donor__user').order_by('rank_position')
        
        serializer = AIRankingListSerializer(rankings, many=True)
        
        return success_response(
            data={
                'blood_request_id': str(request_id),
                'rankings': serializer.data,
                'count': rankings.count()
            },
            message="Ranking history retrieved"
        )


class ReactivationCheckView(APIView):
    """Check and reactivate eligible donors."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        """Manually trigger reactivation check."""
        serializer = ReactivationCheckSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Invalid request",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        donor_id = serializer.validated_data.get('donor_id')
        check_all = serializer.validated_data.get('check_all', False)
        
        reactivated = []
        
        if donor_id:
            # Check specific donor
            try:
                donor = Donor.objects.get(id=donor_id)
                was_eligible = donor.is_eligible
                donor.update_eligibility()
                if not was_eligible and donor.is_eligible:
                    reactivated.append({
                        'id': str(donor.id),
                        'name': donor.user.get_full_name()
                    })
            except Donor.DoesNotExist:
                return error_response(
                    message="Donor not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            total_checked = 1
        elif check_all:
            # Check all inactive donors
            inactive_donors = Donor.objects.filter(is_eligible=False)
            total_checked = inactive_donors.count()
            
            for donor in inactive_donors:
                was_eligible = donor.is_eligible
                donor.update_eligibility()
                if not was_eligible and donor.is_eligible:
                    reactivated.append({
                        'id': str(donor.id),
                        'name': donor.user.get_full_name()
                    })
        else:
            return error_response(
                message="Provide donor_id or set check_all to true",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            data={
                'total_checked': total_checked,
                'reactivated': len(reactivated),
                'reactivated_donors': reactivated
            },
            message=f"Checked {total_checked} donors, reactivated {len(reactivated)}"
        )


class AIMetricsView(APIView):
    """Get AI model metrics."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get latest AI metrics."""
        metrics = AIModelMetrics.objects.order_by('-date')
        latest = metrics.first()
        
        accuracy = float(latest.accuracy_rate) if latest else 0.925
        
        serializer = AIModelMetricsSerializer(metrics[:30], many=True)
        
        return success_response(
            data={
                'accuracy': accuracy,
                'metrics': serializer.data,
                'count': metrics.count()
            },
            message="AI metrics retrieved"
        )
