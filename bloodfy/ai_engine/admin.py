"""
AI Engine app admin configuration.
"""

from django.contrib import admin
from .models import AIRanking, AIModelMetrics


@admin.register(AIRanking)
class AIRankingAdmin(admin.ModelAdmin):
    """AI Ranking admin."""
    
    list_display = ['blood_request', 'donor', 'rank_position', 'final_rank_score', 'was_notified', 'calculated_at']
    list_filter = ['was_notified', 'algorithm_version']
    search_fields = ['donor__user__email']
    readonly_fields = ['calculated_at']


@admin.register(AIModelMetrics)
class AIModelMetricsAdmin(admin.ModelAdmin):
    """AI Model Metrics admin."""
    
    list_display = ['date', 'total_requests', 'successful_matches', 'accuracy_rate']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
