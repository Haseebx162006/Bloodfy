"""
Chatbot app URL routes.
"""

from django.urls import path
from .views import (
    ChatQueryView,
    FAQListView,
    FAQDetailView,
    FAQManagementView,
    ChatFeedbackView,
)

urlpatterns = [
    path('query/', ChatQueryView.as_view(), name='chatbot-query'),
    path('faqs/', FAQListView.as_view(), name='chatbot-faqs'),
    path('faqs/<uuid:faq_id>/', FAQDetailView.as_view(), name='chatbot-faq-detail'),
    path('faqs/manage/', FAQManagementView.as_view(), name='chatbot-faq-create'),
    path('faqs/manage/<uuid:faq_id>/', FAQManagementView.as_view(), name='chatbot-faq-manage'),
    path('feedback/', ChatFeedbackView.as_view(), name='chatbot-feedback'),
]
