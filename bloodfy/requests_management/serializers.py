"""
Requests Management app serializers.
"""

from rest_framework import serializers
from .models import BloodRequest, DonorResponse
from donors.serializers import DonorListSerializer
from recipients.serializers import RecipientListSerializer


class BloodRequestSerializer(serializers.ModelSerializer):
    """Serializer for blood request details."""
    
    recipient_info = RecipientListSerializer(source='recipient', read_only=True)
    matched_donors_count = serializers.SerializerMethodField()
    matched_stock = serializers.SerializerMethodField()
    is_urgent = serializers.BooleanField(read_only=True)
    is_fulfilled = serializers.BooleanField(read_only=True)
    remaining_units = serializers.IntegerField(read_only=True)
    assigned_donor_info = serializers.SerializerMethodField()
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'recipient', 'recipient_info', 'blood_group',
            'units_required', 'units_fulfilled', 'remaining_units',
            'hospital_name', 'hospital_address', 'hospital_city',
            'urgency_level', 'status', 'is_urgent', 'is_fulfilled',
            'patient_name', 'patient_age', 'diagnosis', 'doctor_name',
            'notes', 'is_approved', 'approved_by', 'approved_at',
            'matched_donors_count', 'matched_stock', 'assigned_donor', 'assigned_donor_info',
            'requested_at', 'matched_at', 'assigned_at', 'completed_at', 'cancelled_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'units_fulfilled', 'status', 'is_approved',
            'approved_by', 'approved_at', 'requested_at', 'matched_at',
            'completed_at', 'cancelled_at', 'updated_at'
        ]
    
    def get_matched_donors_count(self, obj):
        return obj.ai_matched_donors.count()
    
    def get_assigned_donor_info(self, obj):
        """Disclosure of donor contact info only after assignment to relevant parties."""
        if not obj.assigned_donor or obj.status != 'assigned':
            return None
        
        request = self.context.get('request')
        if not request:
            return None
            
        request_user = request.user
        
        # Check if user is Admin OR the Recipient (the patient/owner)
        is_owner = hasattr(request_user, 'recipient_profile') and obj.recipient == request_user.recipient_profile
        is_admin = request_user.user_type == 'admin'
        
        if is_admin or is_owner:
            return {
                'name': obj.assigned_donor.user.get_full_name(),
                'phone': obj.assigned_donor.user.phone_number,
                'email': obj.assigned_donor.user.email,
                'city': obj.assigned_donor.city,
                'blood_group': obj.assigned_donor.blood_group
            }
        
        return None
    
    def get_matched_stock(self, obj):
        """Find blood stock that matches this request."""
        from blood_stock.models import BloodStock
        from blood_stock.serializers import BloodStockListSerializer
        from utils.constants import BLOOD_COMPATIBILITY
        
        compatible_groups = BLOOD_COMPATIBILITY.get(obj.blood_group, [obj.blood_group])
        
        stocks = BloodStock.objects.filter(
            blood_group__in=compatible_groups,
            units_available__gt=0,
            hospital_city__icontains=obj.hospital_city
        ).order_by('-units_available')[:5]
        
        return BloodStockListSerializer(stocks, many=True).data


class BloodRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blood requests."""
    
    class Meta:
        model = BloodRequest
        fields = [
            'blood_group', 'units_required',
            'hospital_name', 'hospital_address', 'hospital_city',
            'urgency_level', 'patient_name', 'patient_age',
            'diagnosis', 'doctor_name', 'notes'
        ]
    
    def validate_units_required(self, value):
        """Validate units required."""
        if value < 1:
            raise serializers.ValidationError("At least 1 unit is required.")
        if value > 100:
            raise serializers.ValidationError("Cannot request more than 100 units.")
        return value
    
    def create(self, validated_data):
        """Create blood request for the current user's recipient profile."""
        from recipients.models import Recipient  # Import locally to avoid circular dependency
        user = self.context['request'].user
        
        # Get or Create recipient profile logic
        if not hasattr(user, 'recipient_profile'):
            # Auto-create recipient profile
            recipient = Recipient.objects.create(
                user=user,
                hospital_name=validated_data.get('hospital_name', 'Emergency Individual User'),
                hospital_address=validated_data.get('hospital_address', 'Emergency Address'),
                hospital_city=validated_data.get('hospital_city', user.city or 'Unknown')
            )
        else:
            recipient = user.recipient_profile
        
        # Set default hospital info from recipient profile if not provided
        if not validated_data.get('hospital_name'):
            validated_data['hospital_name'] = recipient.hospital_name
        if not validated_data.get('hospital_address'):
            validated_data['hospital_address'] = recipient.hospital_address
        if not validated_data.get('hospital_city'):
            validated_data['hospital_city'] = recipient.hospital_city
        
        blood_request = BloodRequest.objects.create(
            recipient=recipient,
            **validated_data
        )
        
        # Trigger matching logic
        blood_request.find_matches()
        
        return blood_request


class BloodRequestListSerializer(serializers.ModelSerializer):
    """Serializer for listing blood requests (compact view)."""
    
    recipient_name = serializers.SerializerMethodField()
    recipient_phone = serializers.ReadOnlyField(source='recipient.user.phone_number')
    recipient_user_id = serializers.ReadOnlyField(source='recipient.user.id')
    created_at = serializers.DateTimeField(source='requested_at', read_only=True)
    assigned_donor_info = serializers.SerializerMethodField()
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'recipient_name', 'recipient_phone', 'recipient_user_id', 
            'blood_group', 'units_required', 'units_fulfilled', 
            'hospital_name', 'hospital_city', 'hospital_address',
            'urgency_level', 'status', 'is_urgent', 'is_approved',
            'patient_name', 'patient_age', 'diagnosis', 'notes',
            'assigned_donor_info',
            'requested_at', 'created_at'
        ]
    
    def get_assigned_donor_info(self, obj):
        """Disclosure for list view (reused logic)."""
        # We can reuse the logic from the detail serializer if we want, 
        # but for simplicity let's implement it here as well
        if not obj.assigned_donor or obj.status != 'assigned':
            return None
            
        request = self.context.get('request')
        if not request:
            return None
            
        request_user = request.user
        is_owner = hasattr(request_user, 'recipient_profile') and obj.recipient == request_user.recipient_profile
        is_admin = request_user.user_type == 'admin'
        
        if is_admin or is_owner:
            return {
                'name': obj.assigned_donor.user.get_full_name(),
                'phone': obj.assigned_donor.user.phone_number,
            }
        return None
    
    def get_recipient_name(self, obj):
        name = obj.recipient.user.get_full_name()
        if not name or name.strip() == '':
            return obj.recipient.user.username or obj.recipient.user.email
        return name


class BloodRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blood request."""
    
    class Meta:
        model = BloodRequest
        fields = [
            'units_required', 'urgency_level',
            'patient_name', 'patient_age', 'diagnosis',
            'doctor_name', 'notes'
        ]


class DonorResponseSerializer(serializers.ModelSerializer):
    """Serializer for donor responses."""
    
    donor_info = DonorListSerializer(source='donor', read_only=True)
    
    class Meta:
        model = DonorResponse
        fields = [
            'id', 'blood_request', 'donor', 'donor_info',
            'response_status', 'response_at', 'decline_reason',
            'notified_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'blood_request', 'donor', 'notified_at', 'updated_at'
        ]


class DonorResponseUpdateSerializer(serializers.Serializer):
    """Serializer for updating donor response."""
    
    response_status = serializers.ChoiceField(
        choices=['accepted', 'declined']
    )
    decline_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )
    
    def validate(self, attrs):
        if attrs['response_status'] == 'declined' and not attrs.get('decline_reason'):
            attrs['decline_reason'] = 'No reason provided'
        return attrs


class MatchedDonorsSerializer(serializers.Serializer):
    """Serializer for matched donors list."""
    
    donors = DonorListSerializer(many=True)
    total_count = serializers.IntegerField()
    blood_request_id = serializers.UUIDField()
