"""
Chatbot services - Dialogflow integration and FAQ matching.
"""

import logging
from typing import Optional, Tuple, List
from django.db.models import Q

from .models import FAQ, ChatSession, ChatMessage
from blood_stock.models import BloodStock

logger = logging.getLogger('bloodfy')


class ChatbotService:
    """
    Chatbot service with FAQ matching and basic NLU.
    Falls back to FAQ matching if Dialogflow is not configured.
    """
    
    # Keywords for intent detection
    BLOOD_KEYWORDS = ['blood', 'donate', 'donation', 'donor', 'recipient']
    AVAILABILITY_KEYWORDS = ['available', 'availability', 'check', 'stock', 'units']
    REGISTER_KEYWORDS = ['register', 'signup', 'sign up', 'join', 'become']
    ELIGIBILITY_KEYWORDS = ['eligible', 'eligibility', 'can i donate', 'qualify']
    HELP_KEYWORDS = ['help', 'how', 'what', 'where', 'when']
    
    def __init__(self, user=None):
        self.user = user
    
    def process_query(self, message: str, session_id: str = None) -> dict:
        """
        Process a chat query and return response.
        """
        message_lower = message.lower().strip()
        
        # Try to match FAQ first
        faq_match, confidence = self.match_faq(message_lower)
        
        if faq_match and confidence > 0.5:
            response = faq_match.answer
            intent = 'faq_match'
            
            # Update FAQ view count
            faq_match.view_count += 1
            faq_match.save(update_fields=['view_count'])
        else:
            # Try intent-based response
            response, intent, confidence = self.get_intent_response(message_lower)
            faq_match = None
        
        # Get suggestions
        suggestions = self.get_suggestions(intent)
        
        return {
            'message': response,
            'intent': intent,
            'confidence': confidence,
            'faq_id': str(faq_match.id) if faq_match else None,
            'suggestions': suggestions
        }
    
    def match_faq(self, query: str) -> Tuple[Optional[FAQ], float]:
        """
        Match query against FAQs using keyword matching.
        Returns (FAQ, confidence_score).
        """
        words = set(query.split())
        
        faqs = FAQ.objects.filter(is_active=True)
        best_match = None
        best_score = 0.0
        
        for faq in faqs:
            score = 0.0
            
            # Check keyword match
            keywords = faq.get_keywords_list()
            if keywords:
                keyword_matches = len(words.intersection(set(keywords)))
                score = keyword_matches / max(len(keywords), 1)
            
            # Check question similarity
            faq_words = set(faq.question.lower().split())
            word_overlap = len(words.intersection(faq_words))
            question_score = word_overlap / max(len(faq_words), 1)
            
            score = max(score, question_score)
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        return best_match, best_score
    
    def get_intent_response(self, message: str) -> Tuple[str, str, float]:
        """
        Get response based on detected intent.
        Returns (response, intent, confidence).
        """
        # Check blood availability
        if self._contains_keywords(message, self.AVAILABILITY_KEYWORDS):
            blood_group = self._extract_blood_group(message)
            if blood_group:
                return self._get_blood_availability(blood_group), 'blood_availability', 0.8
            return (
                "Which blood group availability would you like to check? "
                "You can ask like 'Check A+ availability'.",
                'blood_availability_prompt',
                0.6
            )
        
        # Check registration
        if self._contains_keywords(message, self.REGISTER_KEYWORDS):
            if 'donor' in message:
                return (
                    "To register as a donor:\n"
                    "1. Create an account on our website\n"
                    "2. Go to the Donor section\n"
                    "3. Fill in your blood group and contact details\n"
                    "You must be 18+ years old and weigh at least 50kg.",
                    'register_donor',
                    0.8
                )
            return (
                "To register, please visit our website and create an account. "
                "You can register as a Donor or a Recipient (hospital/patient).",
                'register_general',
                0.7
            )
        
        # Check eligibility
        if self._contains_keywords(message, self.ELIGIBILITY_KEYWORDS):
            return (
                "To be eligible to donate blood:\n"
                "• You must be between 18-65 years old\n"
                "• Weigh at least 50kg\n"
                "• Be in good health\n"
                "• Wait 90 days after your last donation\n"
                "• Not have any blood-borne diseases",
                'eligibility_info',
                0.8
            )
        
        # Default response
        return (
            "I'm the Bloodfy assistant! I can help you with:\n"
            "• Checking blood availability\n"
            "• Donor registration information\n"
            "• Donation eligibility\n"
            "• Finding nearby blood banks\n\n"
            "What would you like to know?",
            'greeting',
            0.5
        )
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        return any(kw in text for kw in keywords)
    
    def _extract_blood_group(self, text: str) -> Optional[str]:
        """Extract blood group from text."""
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        text_upper = text.upper()
        
        for bg in blood_groups:
            if bg in text_upper:
                return bg
        return None
    
    def _get_blood_availability(self, blood_group: str) -> str:
        """Get blood availability information."""
        stocks = BloodStock.objects.filter(blood_group=blood_group)
        
        if not stocks.exists():
            return f"No stock information available for {blood_group}. Please contact your nearest blood bank."
        
        response = f"**{blood_group} Blood Availability:**\n\n"
        
        for stock in stocks[:5]:
            status_emoji = "🟢" if not stock.is_low else ("🔴" if stock.is_critical else "🟡")
            response += f"{status_emoji} {stock.hospital_name} ({stock.hospital_city}): {stock.units_available} units\n"
        
        if stocks.count() > 5:
            response += f"\n...and {stocks.count() - 5} more locations."
        
        return response
    
    def get_suggestions(self, intent: str) -> List[str]:
        """Get suggested follow-up questions."""
        suggestions_map = {
            'greeting': [
                "Check O+ availability",
                "How to register as donor?",
                "Am I eligible to donate?"
            ],
            'blood_availability': [
                "Check another blood group",
                "How to donate blood?",
                "Find nearest blood bank"
            ],
            'register_donor': [
                "What are the requirements?",
                "How long does donation take?",
                "Benefits of donating blood"
            ],
            'eligibility_info': [
                "Register as donor",
                "Check blood availability",
                "Contact support"
            ]
        }
        
        return suggestions_map.get(intent, [
            "Check blood availability",
            "Register as donor",
            "Help"
        ])
