"""
Users app serializers.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import User, OTPVerification


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    name = serializers.CharField(required=False, write_only=True)
    cnic = serializers.CharField(required=False, write_only=True)
    address = serializers.CharField(required=False, write_only=True)
    medical_conditions = serializers.CharField(required=False, write_only=True)
    last_donation_date = serializers.DateField(required=False, write_only=True)
    blood_group = serializers.CharField(required=False, write_only=True)
    date_of_birth = serializers.DateField(required=False, write_only=True)
    # Accept any user_type string; create() normalises it to 'user' or 'admin'
    user_type = serializers.CharField(required=False, default='user')

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'name', 'phone_number', 'user_type', 'city',
            'address', 'blood_group', 'date_of_birth', 'cnic',
            'medical_conditions', 'last_donation_date'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'username': {'required': False, 'allow_null': True},
        }
    
    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        # Validate password strength
        try:
            validate_password(attrs['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user (NO automatic donor profile)."""
        name = validated_data.pop('name', None)
        # Remove donor-specific fields (not used during registration)
        validated_data.pop('blood_group', None)
        validated_data.pop('date_of_birth', None)
        validated_data.pop('cnic', None)
        validated_data.pop('medical_conditions', None)
        validated_data.pop('last_donation_date', None)
        
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Handle full name split if first_name/last_name not provided
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        
        if name and not first_name:
            parts = name.split(' ', 1)
            validated_data['first_name'] = parts[0]
            if len(parts) > 1:
                validated_data['last_name'] = parts[1]
            else:
                validated_data['last_name'] = ''

        # Force user_type to 'user' (only admins can create other admins)
        if validated_data.get('user_type') != 'admin':
            validated_data['user_type'] = 'user'
        
        # Ensure user is active by default
        user = User.objects.create_user(
            password=password,
            is_active=True,
            **validated_data
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials."""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    
    full_name = serializers.SerializerMethodField()
    blood_group = serializers.SerializerMethodField()
    is_eligible = serializers.SerializerMethodField()
    donation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'user_type', 'donor_status', 'is_verified', 'is_active',
            'city', 'address', 'profile_picture', 'blood_group',
            'is_eligible', 'donation_count',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'is_active', 'donor_status', 'date_joined', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_blood_group(self, obj):
        """Get blood group from related donor profile if DONOR_APPROVED."""
        if obj.donor_status == 'DONOR_APPROVED' and hasattr(obj, 'donor_profile'):
            return obj.donor_profile.blood_group
        return None

    def get_is_eligible(self, obj):
        """Get eligibility from related donor profile if DONOR_APPROVED."""
        if obj.donor_status == 'DONOR_APPROVED' and hasattr(obj, 'donor_profile'):
            return obj.donor_profile.is_eligible
        return None

    def get_donation_count(self, obj):
        """Get donation count from related donor profile if DONOR_APPROVED."""
        if obj.donor_status == 'DONOR_APPROVED' and hasattr(obj, 'donor_profile'):
            return obj.donor_profile.donation_count
        return 0


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'city', 'address', 'profile_picture'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_current_password(self, value):
        """Validate current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "New passwords do not match."
            })
        
        try:
            validate_password(attrs['new_password'])
        except Exception as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            user = User.objects.get(email__iexact=value)
            self.user = user
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate OTP and passwords."""
        email = attrs.get('email', '').lower()
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': "User not found."})
        
        # Validate OTP
        otp_record = OTPVerification.objects.filter(
            user=user,
            code=otp,
            purpose='password_reset',
            is_used=False
        ).first()
        
        if not otp_record or not otp_record.is_valid:
            raise serializers.ValidationError({'otp': "Invalid or expired OTP."})
        
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        
        try:
            validate_password(attrs['new_password'])
        except Exception as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        """Validate OTP."""
        email = attrs.get('email', '').lower()
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': "User not found."})
        
        otp_record = OTPVerification.objects.filter(
            user=user,
            code=otp,
            purpose='email_verification',
            is_used=False
        ).first()
        
        if not otp_record or not otp_record.is_valid:
            raise serializers.ValidationError({'otp': "Invalid or expired OTP."})
        
        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=['email_verification', 'password_reset'],
        default='email_verification'
    )
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            user = User.objects.get(email__iexact=value)
            self.user = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value.lower()
