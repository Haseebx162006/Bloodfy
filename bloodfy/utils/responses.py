"""
Response helpers for standardized API responses.
"""

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Create a standardized success response.
    """
    return Response({
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code,
        'timestamp': timezone.now().isoformat(),
    }, status=status_code)


def created_response(data=None, message="Created successfully"):
    """
    Create a standardized response for resource creation.
    """
    return success_response(data, message, status.HTTP_201_CREATED)


def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized error response.
    """
    return Response({
        'success': False,
        'message': message,
        'errors': errors or {},
        'status_code': status_code,
        'timestamp': timezone.now().isoformat(),
    }, status=status_code)


def not_found_response(message="Resource not found"):
    """
    Create a standardized not found response.
    """
    return error_response(message, status_code=status.HTTP_404_NOT_FOUND)


def unauthorized_response(message="Authentication required"):
    """
    Create a standardized unauthorized response.
    """
    return error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


def forbidden_response(message="Permission denied"):
    """
    Create a standardized forbidden response.
    """
    return error_response(message, status_code=status.HTTP_403_FORBIDDEN)


def validation_error_response(errors, message="Validation failed"):
    """
    Create a standardized validation error response.
    """
    return error_response(message, errors, status.HTTP_400_BAD_REQUEST)


def paginated_response(data, pagination_info, message="Data retrieved successfully"):
    """
    Create a standardized paginated response.
    """
    return Response({
        'success': True,
        'message': message,
        'data': {
            'results': data,
            'pagination': pagination_info,
        },
        'status_code': status.HTTP_200_OK,
        'timestamp': timezone.now().isoformat(),
    }, status=status.HTTP_200_OK)
