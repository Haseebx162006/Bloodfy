"""
AI Engine app serializers.
"""

from rest_framework import serializers
from .models import AIRanking, AIModelMetrics
from donors.serializers import DonorListSerializer


class AIRankingSerializer(serializers.ModelSerializer):
    """Serializer for AI ranking details."""
    
    donor_info = DonorListSerializer(source='donor', read_only=True)
    
    class Meta:
        model = AIRanking
        fields = [
            'id', 'blood_request', 'donor', 'donor_info',
            'compatibility_score', 'distance_score',
            'responsiveness_score', 'eligibility_score',
            'final_rank_score', 'rank_position', 'distance_km',
            'algorithm_version', 'was_notified', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class AIRankingListSerializer(serializers.ModelSerializer):
    """Serializer for listing AI rankings (compact view)."""
    
    donor_name = serializers.SerializerMethodField()
    donor_blood_group = serializers.CharField(source='donor.blood_group', read_only=True)
    
    class Meta:
        model = AIRanking
        fields = [
            'id', 'donor', 'donor_name', 'donor_blood_group',
            'final_rank_score', 'rank_position', 'distance_km',
            'was_notified', 'calculated_at'
        ]
    
    def get_donor_name(self, obj):
        return obj.donor.user.get_full_name()


class RankDonorsRequestSerializer(serializers.Serializer):
    """Serializer for triggering AI donor ranking."""
    
    blood_request_id = serializers.UUIDField(required=False)
    
    # Matching dashboard frontend keys for preview/simulation
    blood_group_needed = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    urgency_level = serializers.CharField(required=False)
    
    max_donors = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=50
    )
    max_distance_km = serializers.IntegerField(
        default=50,
        min_value=5,
        max_value=200
    )
    include_unavailable = serializers.BooleanField(default=False)


class RankDonorsResponseSerializer(serializers.Serializer):
    """Serializer for AI ranking response."""
    
    blood_request_id = serializers.UUIDField()
    blood_group = serializers.CharField()
    total_eligible_donors = serializers.IntegerField()
    ranked_donors = AIRankingListSerializer(many=True)
    algorithm_version = serializers.CharField()
    calculated_at = serializers.DateTimeField()


class AIModelMetricsSerializer(serializers.ModelSerializer):
    """Serializer for AI model metrics."""
    
    class Meta:
        model = AIModelMetrics
        fields = [
            'id', 'date', 'total_requests', 'successful_matches',
            'accuracy_rate', 'average_response_time_hours',
            'top_1_accuracy', 'top_3_accuracy', 'top_5_accuracy',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReactivationCheckSerializer(serializers.Serializer):
    """Serializer for reactivation check request."""
    
    donor_id = serializers.UUIDField(required=False)
    check_all = serializers.BooleanField(default=False)


class ReactivationResultSerializer(serializers.Serializer):
    """Serializer for reactivation check result."""
    
    total_checked = serializers.IntegerField()
    reactivated = serializers.IntegerField()
    reactivated_donors = serializers.ListField()
