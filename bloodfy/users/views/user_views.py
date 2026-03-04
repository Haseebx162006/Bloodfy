"""
Users app views for user management.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
)
from utils.responses import success_response, error_response
from utils.permissions import IsAdmin


class ProfileView(APIView):
    """Get and update user profile."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's profile."""
        serializer = UserSerializer(request.user)
        
        return success_response(
            data=serializer.data,
            message="Profile retrieved successfully"
        )
    
    def put(self, request):
        """Update current user's profile."""
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Profile update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            data=UserSerializer(request.user).data,
            message="Profile updated successfully"
        )


class ChangePasswordView(APIView):
    """Change user password."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Password change failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        
        return success_response(
            message="Password changed successfully"
        )


class UserListView(APIView):
    """List all users (Admin only)."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        user_type = request.query_params.get('user_type')
        is_verified = request.query_params.get('is_verified')
        
        queryset = User.objects.all()
        
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        serializer = UserSerializer(queryset, many=True)
        
        return success_response(
            data={
                'users': serializer.data,
                'count': queryset.count()
            },
            message="Users retrieved successfully"
        )


    def post(self, request):
        """Create a new user (Admin only)."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="User creation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        return success_response(
            data=UserSerializer(user).data,
            message="User created successfully",
            status_code=status.HTTP_201_CREATED
        )


class UserDetailView(APIView):
    """Get or update specific user details (Admin only)."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserSerializer(user)
        
        return success_response(
            data=serializer.data,
            message="User retrieved successfully"
        )
    
    def put(self, request, user_id):
        """Update a user's details (Admin only)."""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return error_response(
                message="User update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            data=serializer.data,
            message="User updated successfully"
        )
    
    def delete(self, request, user_id):
        """Deactivate a user (Admin only)."""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        return success_response(
            message="User deactivated successfully"
        )
