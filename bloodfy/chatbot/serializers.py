"""
Chatbot app serializers.
"""

from rest_framework import serializers
from .models import FAQ, ChatSession, ChatMessage


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ details."""
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category',
            'keywords', 'priority', 'is_active', 'view_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']


class FAQListSerializer(serializers.ModelSerializer):
    """Serializer for listing FAQs (compact view)."""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'category', 'priority']


class ChatQuerySerializer(serializers.Serializer):
    """Serializer for chatbot query."""
    
    message = serializers.CharField(max_length=1000)
    session_id = serializers.UUIDField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chatbot response."""
    
    message = serializers.CharField()
    intent = serializers.CharField(allow_null=True)
    confidence = serializers.DecimalField(
        max_digits=5,
        decimal_places=4,
        allow_null=True
    )
    session_id = serializers.UUIDField()
    faq_id = serializers.UUIDField(allow_null=True)
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat session."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'user_email', 'session_key',
            'started_at', 'ended_at', 'is_active', 'message_count'
        ]
        read_only_fields = ['id', 'started_at', 'message_count']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'message_type', 'content',
            'intent', 'confidence', 'faq_matched', 'was_helpful',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ChatHistorySerializer(serializers.Serializer):
    """Serializer for chat history response."""
    
    session = ChatSessionSerializer()
    messages = ChatMessageSerializer(many=True)


class FeedbackSerializer(serializers.Serializer):
    """Serializer for chat message feedback."""
    
    message_id = serializers.UUIDField()
    was_helpful = serializers.BooleanField()
