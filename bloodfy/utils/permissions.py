"""
Custom permissions for Bloodfy application.
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users only.
    """
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'admin'
        )


class IsDonor(permissions.BasePermission):
    """
    Permission check for donor users only.
    """
    message = "Only donors can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'donor'
        )


class IsRecipient(permissions.BasePermission):
    """
    Permission check for recipient users only.
    """
    message = "Only recipients can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'recipient'
        )


class IsDonorOrAdmin(permissions.BasePermission):
    """
    Permission check for donor or admin users.
    """
    message = "Only donors or administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['donor', 'admin']
        )


class IsRecipientOrAdmin(permissions.BasePermission):
    """
    Permission check for recipient or admin users.
    """
    message = "Only recipients or administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['recipient', 'admin']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it.
    """
    message = "You can only modify your own data."
    
    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user.user_type == 'admin':
            return True
        
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If the object IS a user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission check for verified users only.
    """
    message = "Please verify your account to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_verified
        )


class ReadOnly(permissions.BasePermission):
    """
    Permission for read-only access.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all authenticated users,
    but write access only to admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'admin'
        )


class AdminWriteOnly(permissions.BasePermission):
    """
    Permission class for endpoints with mixed access:
    - GET: Any authenticated user
    - POST/PUT/DELETE: Admin only
    
    Use this for views where reading is open but modifications are restricted.
    Returns 403 Forbidden with clear message for unauthorized write attempts.
    """
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        # All authenticated users can read
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Only admins can write
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'admin'
        )

