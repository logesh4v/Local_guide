"""
Guard Agent for Local Guide AI.
Responsible for post-processing validation to prevent hallucinations.
"""
import re
import os
import sys
from typing import List, Tuple, Optional, Set

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Response


class GuardAgent:
    """Agent responsible for validating responses and preventing hallucinations."""
    
    def __init__(self):
        """Initialize the Guard Agent."""
        self.standardized_refusals = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        # Common words to ignore during validation
        self.common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'here', 'there',
            'where', 'when', 'why', 'how', 'what', 'who', 'which', 'very', 'much',
            'many', 'most', 'more', 'some', 'any', 'all', 'each', 'every', 'no',
            'not', 'only', 'just', 'also', 'even', 'still', 'well', 'good', 'great',
            'best', 'better', 'nice', 'popular', 'famous', 'known', 'called'
        }
        
        # Suspicious patterns that might indicate hallucination
        self.suspicious_patterns = [
            r'\b(according to|research shows|studies indicate|experts say)\b',
            r'\b(wikipedia|google|internet|online sources)\b',
            r'\b(i think|i believe|in my opinion|personally)\b',
            r'\b(generally|usually|typically|commonly|often)\b',
            r'\b(worldwide|globally|internationally|across india)\b',
            r'\b(modern|contemporary|recent|latest|current)\b'
        ]
    
    def validate_response(self, response: str, context: str) -> bool:
        """
        Validate that response contains only context-based information.
        
        Args:
            response: Generated response text
            context: Source context content
            
        Returns:
            True if response is valid, False if hallucination detected
        """
        if not response or not context:
            return False
        
        # Always allow standardized refusals
        if self._is_standardized_refusal(response):
            return True
        
        # Check for suspicious patterns
        if self._contains_suspicious_patterns(response):
            return False
        
        # Check content overlap with context
        if not self._has_sufficient_context_overlap(response, context):
            return False
        
        # Check for external knowledge indicators
        if self._contains_external_knowledge(response, context):
            return False
        
        return True
    
    def detect_hallucination(self, response: str, context: str) -> bool:
        """
        Detect if response contains hallucinated content.
        
        Args:
            response: Generated response text
            context: Source context content
            
        Returns:
            True if hallucination detected, False otherwise
        """
        return not self.validate_response(response, context)
    
    def force_refusal(self, reason: str) -> str:
        """
        Force a standardized refusal response.
        
        Args:
            reason: Reason for forcing refusal
            
        Returns:
            Standardized refusal message
        """
        # Return the most appropriate refusal based on reason
        if "context" in reason.lower():
            return self.standardized_refusals[0]  # "This isn't covered in my local context."
        elif "data" in reason.lower():
            return self.standardized_refusals[1]  # "I don't have enough local data to answer that."
        else:
            return self.standardized_refusals[2]  # "My knowledge is limited to what's in the context file."
    
    def validate_and_correct_response(self, response: str, context: str) -> Tuple[str, bool]:
        """
        Validate response and correct if necessary.
        
        Args:
            response: Generated response text
            context: Source context content
            
        Returns:
            Tuple of (corrected_response, was_corrected)
        """
        if self.validate_response(response, context):
            return response, False
        else:
            # Force refusal if validation fails
            refusal = self.force_refusal("hallucination detected")
            return refusal, True
    
    def _is_standardized_refusal(self, response: str) -> bool:
        """Check if response is a standardized refusal."""
        return any(refusal in response for refusal in self.standardized_refusals)
    
    def _contains_suspicious_patterns(self, response: str) -> bool:
        """Check if response contains suspicious patterns indicating external knowledge."""
        response_lower = response.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, response_lower):
                return True
        
        return False
    
    def _has_sufficient_context_overlap(self, response: str, context: str, min_overlap: float = 0.3) -> bool:
        """
        Check if response has sufficient overlap with context.
        
        Args:
            response: Response text
            context: Context text
            min_overlap: Minimum overlap ratio required
            
        Returns:
            True if sufficient overlap, False otherwise
        """
        response_words = self._extract_content_words(response)
        context_words = self._extract_content_words(context)
        
        if not response_words:
            return False
        
        overlap = response_words.intersection(context_words)
        overlap_ratio = len(overlap) / len(response_words)
        
        return overlap_ratio >= min_overlap
    
    def _extract_content_words(self, text: str) -> Set[str]:
        """
        Extract content words (excluding common words) from text.
        
        Args:
            text: Input text
            
        Returns:
            Set of content words in lowercase
        """
        if not text:
            return set()
        
        # Extract words and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Remove common words
        content_words = set(word for word in words if word not in self.common_words)
        
        return content_words
    
    def _contains_external_knowledge(self, response: str, context: str) -> bool:
        """
        Check if response contains information not present in context.
        
        Args:
            response: Response text
            context: Context text
            
        Returns:
            True if external knowledge detected, False otherwise
        """
        response_words = self._extract_content_words(response)
        context_words = self._extract_content_words(context)
        
        # Check for significant content words not in context
        external_words = response_words - context_words
        
        # Allow some external words (like connecting words, general terms)
        # But flag if too many specific terms are not in context
        if len(external_words) > len(response_words) * 0.4:  # More than 40% external
            return True
        
        # Check for specific external knowledge indicators
        external_indicators = {
            'wikipedia', 'google', 'internet', 'website', 'online', 'research',
            'study', 'survey', 'report', 'statistics', 'data', 'according',
            'experts', 'scientists', 'government', 'official', 'ministry'
        }
        
        if external_words.intersection(external_indicators):
            return True
        
        return False
    
    def get_validation_details(self, response: str, context: str) -> dict:
        """
        Get detailed validation information for debugging.
        
        Args:
            response: Response text
            context: Context text
            
        Returns:
            Dictionary with validation details
        """
        is_valid = self.validate_response(response, context)
        
        response_words = self._extract_content_words(response)
        context_words = self._extract_content_words(context)
        overlap = response_words.intersection(context_words)
        external_words = response_words - context_words
        
        overlap_ratio = len(overlap) / len(response_words) if response_words else 0
        
        return {
            'is_valid': is_valid,
            'is_refusal': self._is_standardized_refusal(response),
            'has_suspicious_patterns': self._contains_suspicious_patterns(response),
            'overlap_ratio': overlap_ratio,
            'response_word_count': len(response_words),
            'context_word_count': len(context_words),
            'overlap_word_count': len(overlap),
            'external_word_count': len(external_words),
            'external_words': list(external_words)[:10],  # First 10 external words
            'overlap_words': list(overlap)[:10]  # First 10 overlap words
        }
    
    def validate_response_object(self, response_obj: Response, context: str) -> Response:
        """
        Validate a Response object and update its validation status.
        
        Args:
            response_obj: Response object to validate
            context: Source context content
            
        Returns:
            Updated Response object
        """
        is_valid = self.validate_response(response_obj.text, context)
        
        if not is_valid:
            # Force refusal and update response object
            refusal_text = self.force_refusal("validation failed")
            response_obj.text = refusal_text
            response_obj.is_refusal = True
            response_obj.refusal_reason = "Guard agent detected potential hallucination"
            response_obj.validation_passed = False
        else:
            response_obj.validation_passed = True
        
        return response_obj
    
    def batch_validate_responses(self, responses: List[str], context: str) -> List[Tuple[str, bool]]:
        """
        Validate multiple responses in batch.
        
        Args:
            responses: List of response texts
            context: Source context content
            
        Returns:
            List of tuples (response_text, is_valid)
        """
        results = []
        for response in responses:
            is_valid = self.validate_response(response, context)
            results.append((response, is_valid))
        
        return results
    
    def get_refusal_statistics(self, responses: List[str]) -> dict:
        """
        Get statistics about refusal responses.
        
        Args:
            responses: List of response texts
            
        Returns:
            Dictionary with refusal statistics
        """
        total_responses = len(responses)
        refusal_count = sum(1 for response in responses if self._is_standardized_refusal(response))
        
        refusal_breakdown = {}
        for refusal in self.standardized_refusals:
            count = sum(1 for response in responses if refusal in response)
            refusal_breakdown[refusal] = count
        
        return {
            'total_responses': total_responses,
            'refusal_count': refusal_count,
            'refusal_rate': refusal_count / total_responses if total_responses > 0 else 0,
            'refusal_breakdown': refusal_breakdown
        }