"""
Chatbot app admin configuration.
"""

from django.contrib import admin
from .models import FAQ, ChatSession, ChatMessage


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """FAQ admin."""
    
    list_display = ['question_preview', 'category', 'priority', 'view_count', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer', 'keywords']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Chat Session admin."""
    
    list_display = ['id', 'user', 'message_count', 'is_active', 'started_at']
    list_filter = ['is_active']
    search_fields = ['user__email']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Chat Message admin."""
    
    list_display = ['session', 'message_type', 'content_preview', 'intent', 'created_at']
    list_filter = ['message_type', 'intent']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
