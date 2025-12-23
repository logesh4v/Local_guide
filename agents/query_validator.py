"""
Query Validation Agent for Local Guide AI.
Responsible for validating user queries are within supported scope.
"""
import re
import os
import sys
from typing import List, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Query


class QueryValidationAgent:
    """Agent responsible for validating user queries against supported topics."""
    
    def __init__(self):
        """Initialize the Query Validation Agent."""
        self.supported_topics = ['food', 'transport', 'slang', 'safety', 'lifestyle']
        
        # Keywords for each supported topic
        self.topic_keywords = {
            'food': [
                'food', 'eat', 'restaurant', 'meal', 'dish', 'cuisine', 'biryani', 
                'idli', 'dosa', 'curry', 'sweet', 'snack', 'breakfast', 'lunch', 
                'dinner', 'drink', 'tea', 'coffee', 'jigarthanda', 'thalappakatti',
                'hotel', 'mess', 'cooking', 'recipe', 'taste', 'spicy', 'traditional'
            ],
            'transport': [
                'transport', 'bus', 'auto', 'rickshaw', 'taxi', 'train', 'railway',
                'station', 'route', 'travel', 'journey', 'fare', 'ticket', 'road',
                'highway', 'airport', 'metro', 'share', 'vehicle', 'driving', 'walk'
            ],
            'slang': [
                'slang', 'language', 'phrase', 'word', 'speak', 'say', 'call',
                'meaning', 'tamil', 'local', 'dialect', 'accent', 'expression',
                'greeting', 'common', 'people say', 'how to say', 'what does',
                'pronunciation', 'conversation'
            ],
            'safety': [
                'safety', 'safe', 'danger', 'crime', 'police', 'emergency', 'help',
                'secure', 'avoid', 'careful', 'precaution', 'risk', 'problem',
                'trouble', 'area', 'night', 'alone', 'tourist', 'scam', 'theft',
                'hospital', 'ambulance', 'fire'
            ],
            'lifestyle': [
                'lifestyle', 'culture', 'custom', 'tradition', 'festival', 'celebration',
                'shopping', 'market', 'temple', 'worship', 'dress', 'clothing',
                'weather', 'climate', 'season', 'people', 'behavior', 'etiquette',
                'social', 'family', 'marriage', 'business', 'work', 'education',
                'entertainment', 'music', 'dance', 'art', 'history', 'things', 'try',
                'do', 'visit', 'see', 'experience', 'activity', 'activities', 'now',
                'today', 'currently', 'what', 'where', 'when', 'recommend', 'suggest'
            ]
        }
    
    def get_supported_topics(self) -> List[str]:
        """
        Get list of supported topics.
        
        Returns:
            List of supported topic names
        """
        return self.supported_topics.copy()
    
    def is_supported_topic(self, query: str) -> bool:
        """
        Check if query is about a supported topic.
        
        Args:
            query: User query text
            
        Returns:
            True if query is about supported topic, False otherwise
        """
        if not query or not query.strip():
            return False
        
        query_lower = query.lower()
        
        # Allow general queries about the cities themselves
        city_names = ['madurai', 'dindigul']
        general_city_queries = [
            'tell me about', 'what about', 'about', 'describe', 'information',
            'know about', 'learn about', 'explain', 'overview', 'guide'
        ]
        
        # Check if it's a general query about one of the supported cities
        for city in city_names:
            if city in query_lower:
                for general_phrase in general_city_queries:
                    if general_phrase in query_lower:
                        return True
        
        # Check if query contains keywords from any supported topic
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return True
        
        return False
    
    def identify_topic(self, query: str) -> Optional[str]:
        """
        Identify which topic the query is about.
        
        Args:
            query: User query text
            
        Returns:
            Topic name if identified, None otherwise
        """
        if not query or not query.strip():
            return None
        
        query_lower = query.lower()
        topic_scores = {topic: 0 for topic in self.supported_topics}
        
        # Score each topic based on keyword matches
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Give higher score for exact word matches
                    if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                        topic_scores[topic] += 2
                    else:
                        topic_scores[topic] += 1
        
        # Return topic with highest score, if any
        max_score = max(topic_scores.values())
        if max_score > 0:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    
    def validate_query_scope(self, query: str) -> bool:
        """
        Validate if query is within supported scope.
        
        Args:
            query: User query text
            
        Returns:
            True if query is valid and in scope, False otherwise
        """
        # Check for empty or whitespace-only queries
        if not query or not query.strip():
            return False
        
        # Check if query is too long (potential spam or abuse)
        if len(query) > 1000:
            return False
        
        # Check if query contains only special characters or numbers
        if re.match(r'^[^a-zA-Z]*$', query.strip()):
            return False
        
        # Check if query is about supported topics
        return self.is_supported_topic(query)
    
    def get_rejection_reason(self, query: str) -> str:
        """
        Get reason for query rejection.
        
        Args:
            query: User query text
            
        Returns:
            Reason for rejection
        """
        if not query or not query.strip():
            return "Query is empty or contains only whitespace."
        
        if len(query) > 1000:
            return "Query is too long. Please keep questions concise."
        
        if re.match(r'^[^a-zA-Z]*$', query.strip()):
            return "Query contains only special characters or numbers."
        
        if not self.is_supported_topic(query):
            supported_topics_str = ", ".join(self.supported_topics)
            return f"Query is outside supported topics. I can help with: {supported_topics_str}."
        
        return "Query validation failed for unknown reason."
    
    def validate_query_object(self, query: Query) -> Tuple[bool, Optional[str]]:
        """
        Validate a Query object.
        
        Args:
            query: Query object to validate
            
        Returns:
            Tuple of (is_valid, rejection_reason)
        """
        if query.is_empty():
            return False, "Query is empty."
        
        is_valid = self.validate_query_scope(query.text)
        rejection_reason = None if is_valid else self.get_rejection_reason(query.text)
        
        return is_valid, rejection_reason
    
    def preprocess_query(self, query_text: str) -> str:
        """
        Preprocess query text for better validation.
        
        Args:
            query_text: Raw query text
            
        Returns:
            Preprocessed query text
        """
        if not query_text:
            return ""
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', query_text.strip())
        
        # Remove excessive punctuation
        processed = re.sub(r'[!?]{3,}', '?', processed)
        processed = re.sub(r'\.{3,}', '...', processed)
        
        return processed
    
    def get_topic_suggestions(self, query: str) -> List[str]:
        """
        Get topic suggestions for out-of-scope queries.
        
        Args:
            query: User query text
            
        Returns:
            List of suggested topics that might be relevant
        """
        if not query:
            return self.supported_topics.copy()
        
        query_lower = query.lower()
        suggestions = []
        
        # Look for partial matches or related terms
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if any(word in keyword for word in query_lower.split()):
                    if topic not in suggestions:
                        suggestions.append(topic)
                    break
        
        # If no suggestions found, return all topics
        if not suggestions:
            suggestions = self.supported_topics.copy()
        
        return suggestions
    
    def create_validation_response(self, query_text: str, city: str) -> Query:
        """
        Create a validated Query object.
        
        Args:
            query_text: Raw query text
            city: Selected city
            
        Returns:
            Query object with validation results
        """
        from datetime import datetime
        
        processed_query = self.preprocess_query(query_text)
        is_valid, rejection_reason = self.validate_query_scope(processed_query), None
        
        if not is_valid:
            rejection_reason = self.get_rejection_reason(processed_query)
        
        return Query(
            text=processed_query,
            city=city,
            timestamp=datetime.now(),
            is_valid=is_valid,
            validation_reason=rejection_reason
        )