"""
Recipients app serializers.
"""

from rest_framework import serializers
from .models import Recipient
from users.serializers import UserSerializer


class RecipientSerializer(serializers.ModelSerializer):
    """Serializer for recipient details."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Recipient
        fields = [
            'id', 'user', 'hospital_name', 'hospital_address',
            'hospital_city', 'latitude', 'longitude',
            'emergency_contact', 'secondary_contact',
            'patient_name', 'patient_age', 'doctor_name', 'department',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipientRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for recipient registration."""
    
    class Meta:
        model = Recipient
        fields = [
            'hospital_name', 'hospital_address', 'hospital_city',
            'latitude', 'longitude', 'emergency_contact', 'secondary_contact',
            'patient_name', 'patient_age', 'doctor_name', 'department'
        ]
    
    def create(self, validated_data):
        """Create recipient profile for the current user."""
        user = self.context['request'].user
        
        # Check if user already has a recipient profile
        if hasattr(user, 'recipient_profile'):
            raise serializers.ValidationError("User already has a recipient profile.")
        
        # Update user type
        user.user_type = 'recipient'
        user.save(update_fields=['user_type'])
        
        recipient = Recipient.objects.create(user=user, **validated_data)
        return recipient


class RecipientUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating recipient profile."""
    
    class Meta:
        model = Recipient
        fields = [
            'hospital_name', 'hospital_address', 'hospital_city',
            'latitude', 'longitude', 'emergency_contact', 'secondary_contact',
            'patient_name', 'patient_age', 'doctor_name', 'department'
        ]


class RecipientListSerializer(serializers.ModelSerializer):
    """Serializer for listing recipients (compact view)."""
    
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Recipient
        fields = [
            'id', 'name', 'email', 'hospital_name',
            'hospital_city', 'is_active'
        ]
    
    def get_name(self, obj):
        return obj.user.get_full_name()
