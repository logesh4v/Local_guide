"""
Standardized Refusal Response Handler for Local Guide AI.
Ensures consistent refusal responses across the application.
"""
import random
from typing import List, Optional
from enum import Enum


class RefusalReason(Enum):
    """Enumeration of refusal reasons."""
    MISSING_CONTEXT = "missing_context"
    INSUFFICIENT_DATA = "insufficient_data" 
    GENERAL_LIMITATION = "general_limitation"
    OUT_OF_SCOPE = "out_of_scope"
    VALIDATION_FAILED = "validation_failed"


class RefusalHandler:
    """Handler for generating standardized refusal responses."""
    
    def __init__(self):
        """Initialize the refusal handler with standardized phrases."""
        self.standardized_phrases = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        # Map reasons to preferred phrases
        self.reason_to_phrase = {
            RefusalReason.MISSING_CONTEXT: self.standardized_phrases[0],
            RefusalReason.INSUFFICIENT_DATA: self.standardized_phrases[1],
            RefusalReason.GENERAL_LIMITATION: self.standardized_phrases[2],
            RefusalReason.OUT_OF_SCOPE: self.standardized_phrases[0],
            RefusalReason.VALIDATION_FAILED: self.standardized_phrases[2]
        }
    
    def get_standardized_phrases(self) -> List[str]:
        """
        Get list of all standardized refusal phrases.
        
        Returns:
            List of standardized refusal phrases
        """
        return self.standardized_phrases.copy()
    
    def is_standardized_refusal(self, response: str) -> bool:
        """
        Check if response is a standardized refusal.
        
        Args:
            response: Response text to check
            
        Returns:
            True if response is standardized refusal, False otherwise
        """
        if not response:
            return False
        
        return any(phrase in response for phrase in self.standardized_phrases)
    
    def get_refusal_by_reason(self, reason: RefusalReason) -> str:
        """
        Get appropriate refusal phrase for specific reason.
        
        Args:
            reason: Reason for refusal
            
        Returns:
            Appropriate standardized refusal phrase
        """
        return self.reason_to_phrase.get(reason, self.standardized_phrases[2])
    
    def get_refusal_by_keyword(self, keyword: str) -> str:
        """
        Get appropriate refusal phrase based on keyword in reason.
        
        Args:
            keyword: Keyword indicating reason for refusal
            
        Returns:
            Appropriate standardized refusal phrase
        """
        keyword_lower = keyword.lower()
        
        if "context" in keyword_lower:
            return self.standardized_phrases[0]
        elif "data" in keyword_lower:
            return self.standardized_phrases[1]
        else:
            return self.standardized_phrases[2]
    
    def get_random_refusal(self) -> str:
        """
        Get a random standardized refusal phrase.
        
        Returns:
            Random standardized refusal phrase
        """
        return random.choice(self.standardized_phrases)
    
    def validate_refusal_format(self, response: str) -> bool:
        """
        Validate that refusal response uses exact standardized format.
        
        Args:
            response: Response to validate
            
        Returns:
            True if exact match with standardized phrase, False otherwise
        """
        if not response:
            return False
        
        # Check for exact matches (allowing for whitespace differences)
        response_clean = response.strip()
        return response_clean in self.standardized_phrases
    
    def correct_refusal_format(self, response: str) -> Optional[str]:
        """
        Correct refusal response to use standardized format.
        
        Args:
            response: Response that might be a malformed refusal
            
        Returns:
            Corrected standardized refusal or None if not a refusal
        """
        if not response:
            return None
        
        response_lower = response.lower()
        
        # Check for partial matches and correct them
        if "context" in response_lower and ("cover" in response_lower or "local" in response_lower):
            return self.standardized_phrases[0]
        elif "data" in response_lower and ("enough" in response_lower or "local" in response_lower):
            return self.standardized_phrases[1]
        elif "knowledge" in response_lower and ("limited" in response_lower or "context" in response_lower):
            return self.standardized_phrases[2]
        
        return None
    
    def get_refusal_statistics(self, responses: List[str]) -> dict:
        """
        Get statistics about refusal usage in responses.
        
        Args:
            responses: List of response texts
            
        Returns:
            Dictionary with refusal statistics
        """
        total_responses = len(responses)
        refusal_count = 0
        phrase_counts = {phrase: 0 for phrase in self.standardized_phrases}
        malformed_refusals = 0
        
        for response in responses:
            if self.is_standardized_refusal(response):
                refusal_count += 1
                
                # Count specific phrases
                for phrase in self.standardized_phrases:
                    if phrase in response:
                        phrase_counts[phrase] += 1
                        break
            elif self.correct_refusal_format(response):
                # This is a malformed refusal
                malformed_refusals += 1
        
        return {
            'total_responses': total_responses,
            'refusal_count': refusal_count,
            'refusal_rate': refusal_count / total_responses if total_responses > 0 else 0,
            'phrase_distribution': phrase_counts,
            'malformed_refusals': malformed_refusals,
            'most_used_phrase': max(phrase_counts, key=phrase_counts.get) if any(phrase_counts.values()) else None
        }
    
    def ensure_standardized_refusal(self, response: str, reason: Optional[RefusalReason] = None) -> str:
        """
        Ensure response is a properly formatted standardized refusal.
        
        Args:
            response: Original response
            reason: Optional reason for refusal
            
        Returns:
            Standardized refusal response
        """
        # If already standardized, return as-is
        if self.validate_refusal_format(response):
            return response
        
        # If it's a malformed refusal, correct it
        corrected = self.correct_refusal_format(response)
        if corrected:
            return corrected
        
        # Otherwise, generate new refusal based on reason
        if reason:
            return self.get_refusal_by_reason(reason)
        else:
            return self.standardized_phrases[2]  # Default to general limitation
    
    def create_refusal_response(self, 
                              reason: RefusalReason = RefusalReason.GENERAL_LIMITATION,
                              context_info: Optional[str] = None) -> str:
        """
        Create a standardized refusal response.
        
        Args:
            reason: Reason for the refusal
            context_info: Optional context information (not used in current implementation)
            
        Returns:
            Standardized refusal response
        """
        return self.get_refusal_by_reason(reason)
    
    def is_refusal_appropriate(self, query: str, context: str) -> bool:
        """
        Determine if a refusal response would be appropriate.
        
        Args:
            query: User query
            context: Available context
            
        Returns:
            True if refusal is appropriate, False otherwise
        """
        if not query or not query.strip():
            return True
        
        if not context or not context.strip():
            return True
        
        # Basic heuristic: if query contains words not in context, refusal might be appropriate
        query_words = set(query.lower().split())
        context_words = set(context.lower().split())
        
        # Remove common words for better analysis
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        query_content = query_words - common_words
        context_content = context_words - common_words
        
        if not query_content:
            return False  # Query has no meaningful content
        
        # If less than 30% of query words are in context, refusal might be appropriate
        overlap = query_content.intersection(context_content)
        overlap_ratio = len(overlap) / len(query_content)
        
        return overlap_ratio < 0.3


# Global instance for easy access
refusal_handler = RefusalHandler()