"""
Property-based tests for standardized refusal responses.
**Feature: local-guide-ai, Property 4: Standardized refusal responses**
**Validates: Requirements 3.1, 3.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from refusal_handler import RefusalHandler
from models import Response


class TestStandardizedRefusalsProperty:
    """Property-based tests for standardized refusal responses."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.refusal_handler = RefusalHandler()
    
    @given(st.sampled_from([
        "context missing",
        "insufficient data",
        "validation failed",
        "out of scope",
        "no information available",
        "external knowledge detected",
        "hallucination prevented"
    ]))
    @settings(max_examples=100)
    def test_standardized_refusal_consistency(self, reason: str):
        """
        **Feature: local-guide-ai, Property 4: Standardized refusal responses**
        For any refusal reason, the system should return one of exactly three 
        standardized refusal messages consistently.
        """
        # Get refusal response
        refusal_response = self.refusal_handler.get_refusal_response(reason)
        
        # Should be one of the three standardized responses
        expected_refusals = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        assert refusal_response in expected_refusals, f"Refusal '{refusal_response}' not in standardized list"
        
        # Should be consistent across multiple calls
        second_response = self.refusal_handler.get_refusal_response(reason)
        assert refusal_response == second_response, "Refusal response should be consistent"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_refusal_detection_property(self, text: str):
        """
        Test that refusal detection works correctly for any text.
        """
        assume(text.strip())  # Skip empty strings
        
        is_refusal = self.refusal_handler.is_refusal_response(text)
        
        # Should only detect actual standardized refusals
        expected_refusals = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        if is_refusal:
            assert text in expected_refusals, f"'{text}' detected as refusal but not in standardized list"
        else:
            assert text not in expected_refusals, f"'{text}' not detected as refusal but is in standardized list"
    
    def test_all_refusal_types_covered(self):
        """
        Test that all refusal types return standardized responses.
        """
        refusal_reasons = [
            "context",
            "data", 
            "information",
            "knowledge",
            "scope",
            "validation",
            "hallucination",
            "external",
            "missing",
            "unavailable"
        ]
        
        expected_refusals = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        for reason in refusal_reasons:
            refusal = self.refusal_handler.get_refusal_response(reason)
            assert refusal in expected_refusals, f"Reason '{reason}' produced non-standard refusal: '{refusal}'"
    
    def test_refusal_response_object_creation(self):
        """
        Test creation of Response objects with refusal information.
        """
        reason = "test reason"
        response_obj = self.refusal_handler.create_refusal_response(reason, "Madurai")
        
        assert isinstance(response_obj, Response)
        assert response_obj.is_refusal
        assert response_obj.refusal_reason is not None
        assert response_obj.is_standardized_refusal()
        assert response_obj.text in [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
    
    def test_refusal_statistics(self):
        """
        Test refusal statistics tracking.
        """
        responses = [
            "This isn't covered in my local context.",
            "Normal response about food",
            "I don't have enough local data to answer that.",
            "Another normal response",
            "My knowledge is limited to what's in the context file.",
            "This isn't covered in my local context."
        ]
        
        stats = self.refusal_handler.get_refusal_statistics(responses)
        
        assert stats['total_responses'] == 6
        assert stats['refusal_count'] == 4
        assert stats['refusal_rate'] == 4/6
        
        # Check breakdown
        breakdown = stats['refusal_breakdown']
        assert breakdown["This isn't covered in my local context."] == 2
        assert breakdown["I don't have enough local data to answer that."] == 1
        assert breakdown["My knowledge is limited to what's in the context file."] == 1
    
    @given(st.sampled_from([
        "This isn't covered in my local context.",
        "I don't have enough local data to answer that.",
        "My knowledge is limited to what's in the context file."
    ]))
    @settings(max_examples=50)
    def test_exact_refusal_matching(self, refusal_text: str):
        """
        Test that exact refusal matching works correctly.
        """
        # Exact match should be detected
        assert self.refusal_handler.is_refusal_response(refusal_text)
        
        # Case variations should not be detected (exact match only)
        assert not self.refusal_handler.is_refusal_response(refusal_text.upper())
        assert not self.refusal_handler.is_refusal_response(refusal_text.lower())
        
        # With extra whitespace should not be detected (exact match only)
        assert not self.refusal_handler.is_refusal_response(f" {refusal_text} ")
        assert not self.refusal_handler.is_refusal_response(f"{refusal_text}\n")
    
    def test_refusal_reason_mapping(self):
        """
        Test that different reasons map to appropriate refusal messages.
        """
        # Context-related reasons
        context_reasons = ["context", "local context", "context missing"]
        for reason in context_reasons:
            refusal = self.refusal_handler.get_refusal_response(reason)
            assert refusal == "This isn't covered in my local context."
        
        # Data-related reasons
        data_reasons = ["data", "insufficient data", "no data", "data missing"]
        for reason in data_reasons:
            refusal = self.refusal_handler.get_refusal_response(reason)
            assert refusal == "I don't have enough local data to answer that."
        
        # General knowledge reasons
        knowledge_reasons = ["knowledge", "information", "scope", "validation"]
        for reason in knowledge_reasons:
            refusal = self.refusal_handler.get_refusal_response(reason)
            assert refusal == "My knowledge is limited to what's in the context file."


if __name__ == "__main__":
    pytest.main([__file__])