"""
Recipients app views.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Recipient
from .serializers import (
    RecipientSerializer, RecipientListSerializer,
    RecipientRegistrationSerializer, RecipientUpdateSerializer
)
from utils.responses import success_response, error_response, created_response
from utils.permissions import IsAdmin


class RecipientRegisterView(APIView):
    """Register current user as a recipient."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = RecipientRegistrationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Recipient registration failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        recipient = serializer.save()
        
        return created_response(
            data=RecipientSerializer(recipient).data,
            message="Recipient profile created successfully"
        )


class RecipientProfileView(APIView):
    """Get and update current user's recipient profile."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's recipient profile."""
        if not hasattr(request.user, 'recipient_profile'):
            return error_response(
                message="You are not registered as a recipient",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RecipientSerializer(request.user.recipient_profile)
        return success_response(
            data=serializer.data,
            message="Recipient profile retrieved"
        )
    
    def put(self, request):
        """Update current user's recipient profile."""
        if not hasattr(request.user, 'recipient_profile'):
            return error_response(
                message="You are not registered as a recipient",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        recipient = request.user.recipient_profile
        serializer = RecipientUpdateSerializer(
            recipient,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            data=RecipientSerializer(recipient).data,
            message="Recipient profile updated"
        )


class RecipientListView(APIView):
    """List all recipients (Admin only)."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """List all recipients."""
        queryset = Recipient.objects.select_related('user').all()
        
        # Apply filters
        city = request.query_params.get('city')
        hospital = request.query_params.get('hospital')
        
        if city:
            queryset = queryset.filter(hospital_city__icontains=city)
        if hospital:
            queryset = queryset.filter(hospital_name__icontains=hospital)
        
        serializer = RecipientListSerializer(queryset, many=True)
        
        return success_response(
            data={
                'recipients': serializer.data,
                'count': queryset.count()
            },
            message="Recipients retrieved successfully"
        )


class RecipientDetailView(APIView):
    """Get recipient details (Admin only)."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, recipient_id):
        try:
            recipient = Recipient.objects.select_related('user').get(id=recipient_id)
        except Recipient.DoesNotExist:
            return error_response(
                message="Recipient not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RecipientSerializer(recipient)
        return success_response(
            data=serializer.data,
            message="Recipient retrieved"
        )
