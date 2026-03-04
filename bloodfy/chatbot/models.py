"""
Chatbot app models.
"""

import uuid
from django.db import models
from django.conf import settings


class FAQ(models.Model):
    """
    Frequently Asked Questions for the chatbot.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    question = models.TextField(
        verbose_name='Question'
    )
    
    answer = models.TextField(
        verbose_name='Answer'
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Category'
    )
    
    keywords = models.TextField(
        blank=True,
        null=True,
        help_text='Comma-separated keywords for matching',
        verbose_name='Keywords'
    )
    
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name='Display Priority'
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='View Count'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['-priority', '-view_count']
    
    def __str__(self):
        return self.question[:50]
    
    def get_keywords_list(self):
        """Get keywords as a list."""
        if not self.keywords:
            return []
        return [k.strip().lower() for k in self.keywords.split(',')]


class ChatSession(models.Model):
    """
    Track chatbot sessions.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    
    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Anonymous Session Key'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    # Session metrics
    message_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        user_info = self.user.email if self.user else 'Anonymous'
        return f"Session {str(self.id)[:8]} - {user_info}"


class ChatMessage(models.Model):
    """
    Individual chat messages.
    """
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default='user'
    )
    
    content = models.TextField(
        verbose_name='Message Content'
    )
    
    # For bot responses - track intent matching
    intent = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Detected Intent'
    )
    
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='Intent Confidence'
    )
    
    faq_matched = models.ForeignKey(
        FAQ,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matched_messages'
    )
    
    # Feedback
    was_helpful = models.BooleanField(
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}"
