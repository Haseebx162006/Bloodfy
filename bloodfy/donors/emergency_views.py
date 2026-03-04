"""
Emergency blood search views.
Handles emergency donor search and contact functionality.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

from .models import Donor
from .serializers import DonorListSerializer
from utils.responses import success_response, error_response


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


class EmergencyDonorSearchView(APIView):
    """
    Search for emergency donors by blood group and location.
    Only returns APPROVED and AVAILABLE donors.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/emergency/search?blood_group=O-&location=Lahore
        """
        blood_group = request.query_params.get('blood_group')
        location = request.query_params.get('location')
        
        # Validate required parameters
        if not blood_group:
            return error_response(
                message="Blood group is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not location:
            return error_response(
                message="Location is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Query approved and available donors
        queryset = Donor.objects.select_related('user').filter(
            user__donor_status='DONOR_APPROVED',
            blood_group=blood_group,
            is_active=True,
            availability_status=True,
            city__icontains=location
        )
        
        # Get user's location if available (for distance calculation)
        user_lat = request.query_params.get('latitude')
        user_lon = request.query_params.get('longitude')
        
        results = []
        
        for donor in queryset:
            donor_data = {
                'id': str(donor.id),
                'name': donor.user.get_full_name(),
                'blood_group': donor.blood_group,
                'city': donor.city,
                'phone_number': donor.user.phone_number if donor.user.phone_number else None,
                'distance': None,
                'has_coordinates': bool(donor.latitude and donor.longitude)
            }
            
            # Calculate distance if coordinates are available
            if (user_lat and user_lon and 
                donor.latitude and donor.longitude):
                try:
                    distance = haversine_distance(
                        user_lat, user_lon,
                        donor.latitude, donor.longitude
                    )
                    donor_data['distance'] = round(distance, 2)
                except Exception as e:
                    print(f"Distance calculation error: {e}")
                    donor_data['distance'] = None
            
            results.append(donor_data)
        
        # Sort by distance if available, otherwise by name
        if any(r['distance'] is not None for r in results):
            results.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        else:
            results.sort(key=lambda x: x['name'])
        
        return success_response(
            data={
                'donors': results,
                'count': len(results),
                'blood_group': blood_group,
                'location': location
            },
            message=f"Found {len(results)} donor(s) for {blood_group} in {location}"
        )


class EmergencyContactView(APIView):
    """
    Trigger emergency contact to a donor.
    Logs the contact attempt.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/emergency/contact
        Body: {
            "donor_id": "uuid",
            "contact_type": "SMS" or "CALL"
        }
        """
        donor_id = request.data.get('donor_id')
        contact_type = request.data.get('contact_type', 'CALL')
        
        # Validate donor_id
        if not donor_id:
            return error_response(
                message="Donor ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate contact_type
        if contact_type not in ['SMS', 'CALL']:
            return error_response(
                message="Contact type must be 'SMS' or 'CALL'",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get donor
        try:
            donor = Donor.objects.select_related('user').get(
                id=donor_id,
                user__donor_status='DONOR_APPROVED',
                is_active=True
            )
        except Donor.DoesNotExist:
            return error_response(
                message="Donor not found or not available",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Log contact attempt (in production, this would trigger actual SMS/Call)
        contact_info = {
            'donor_name': donor.user.get_full_name(),
            'donor_phone': donor.user.phone_number,
            'contact_type': contact_type,
            'requested_by': request.user.get_full_name(),
            'requested_by_phone': request.user.phone_number
        }
        
        # In production, you would:
        # - Send SMS via Twilio/AWS SNS
        # - Initiate call via Twilio
        # - Log to database for tracking
        
        print(f"[EMERGENCY CONTACT] {contact_type} to {donor.user.get_full_name()} by {request.user.get_full_name()}")
        
        return success_response(
            data=contact_info,
            message=f"{contact_type} contact initiated successfully"
        )
