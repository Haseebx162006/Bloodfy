"""
Requests Management app admin configuration.
"""

from django.contrib import admin
from .models import BloodRequest, DonorResponse


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    """Blood Request admin."""
    
    list_display = ['id', 'blood_group', 'units_required', 'urgency_level', 'status', 'is_approved', 'requested_at']
    list_filter = ['blood_group', 'urgency_level', 'status', 'is_approved']
    search_fields = ['hospital_name', 'patient_name', 'recipient__user__email']
    readonly_fields = ['requested_at', 'matched_at', 'completed_at']
    
    actions = ['approve_requests', 'mark_as_completed', 'cancel_requests']
    
    def get_short_id(self, obj):
        return str(obj.id)[:8]
    get_short_id.short_description = 'ID'

    @admin.action(description='Approve selected requests')
    def approve_requests(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            is_approved=True, 
            approved_by=request.user, 
            approved_at=timezone.now()
        )
        self.message_user(request, f"{count} requests marked as approved.")

    @admin.action(description='Mark selected requests as Completed')
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            status='completed', 
            completed_at=timezone.now()
        )
        self.message_user(request, f"{count} requests marked as completed.")

    @admin.action(description='Cancel selected requests (Soft Delete)')
    def cancel_requests(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            status='cancelled', 
            cancelled_at=timezone.now()
        )
        self.message_user(request, f"{count} requests marked as cancelled.")


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    """Donor Response admin."""
    
    list_display = ['blood_request', 'donor', 'response_status', 'notified_at']
    list_filter = ['response_status']
    search_fields = ['donor__user__email']
